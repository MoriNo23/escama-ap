/*
 * escama-launch - launcher rootless del AP escama.
 *
 * Por que existe: el kernel ignora las file capabilities en scripts con
 * shebang (execve(2)), asi que el modo sin root necesita un binario ELF. Este
 * launcher recibe las capabilities por `setcap`, se las pasa al proceso Python
 * mediante el set ambient, y ejecuta el nucleo.
 *
 * Receta (capabilities(7), verificada end-to-end en la maquina de desarrollo):
 *   1. setcap cap_net_admin,cap_net_raw,cap_net_bind_service+ep escama-launch
 *   2. sumar esas caps al set INHERITABLE del proceso: en execve el inheritable
 *      NO se toma del archivo (P'(inheritable) = P(inheritable)), asi que
 *      `setcap +ei` no sirve para un usuario normal cuyo inheritable esta vacio.
 *      Sumarlo es legal sin CAP_SETPCAP porque el nuevo set es subconjunto del
 *      permitted (seccion "Programmatically adjusting capability sets").
 *   3. elevarlas a AMBIENT con prctl(PR_CAP_AMBIENT_RAISE): el invariante exige
 *      que la cap este en permitted E inheritable. El ambient sobrevive al
 *      execve de un binario no privilegiado y se suma al permitted del proceso
 *      siguiente (el nucleo Python, que no tiene file capabilities).
 *
 * Decision de implementacion: se usan capset()/prctl() CRUDOS y no libcap,
 * porque la
 * libcap 2.75 de Debian declara cap_set_ambient() con un cap_flag_value_t propio
 * (RAISE == 0, no el opcode 2 de prctl) y aun asi devuelve exito sin elevar el
 * ambient. Medido en esta maquina.
 *
 * Condiciones de install.sh (MUST respetarse, si no falla en silencio):
 *   - el binario debe quedar con owner del usuario que lo ejecuta: si es de root,
 *     el kernel lo trata como "capability-dumb binary" y descarta las caps;
 *   - el chown debe ocurrir ANTES del setcap: chown borra la xattr
 *     security.capability;
 *   - debe vivir en un filesystem que aplique file capabilities (ext4 si;
 *     tmpfs no las aplica aunque getcap las muestre).
 *
 * Uso: escama-launch <comando> [args...]
 * Este launcher no interpreta argumentos propios: solo ejecuta lo que se le pasa.
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/capability.h>

/* Rutas absolutas del interprete y del nucleo. El launcher se usa tambien como
 * punto de re-ejecucion del propio core en modo rootless, y ahi no se puede
 * depender del argv[0] ni del PATH. */
#define ESCAMA_PYTHON "/usr/bin/python3"
#define ESCAMA_CORE   "/opt/escama/escama.py"

/* Capabilities necesarias para operar el AP sin root:
 *   CAP_NET_ADMIN        - ip addr/link, iptables/nft, tabla de rutas, sysctl
 *   CAP_NET_RAW          - sockets raw/packet (hostapd, netlink)
 *   CAP_NET_BIND_SERVICE - dnsmasq binds el 67 (DHCP) y 53 (DNS) */
#define ESCAMA_CAPS ((1u << CAP_NET_ADMIN) | (1u << CAP_NET_RAW) | \
                     (1u << CAP_NET_BIND_SERVICE))

static const int escama_cap_list[] = {CAP_NET_ADMIN, CAP_NET_RAW,
                                      CAP_NET_BIND_SERVICE};

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr,
                "escama-launch: falta el comando a ejecutar\n"
                "uso: escama-launch <comando> [args...]\n");
        return 2;
    }

    /* 1) sumar las caps al inheritable (no hay CAP_SETPCAP, pero el set nuevo
     *    es subconjunto del permitted que vino por file caps) */
    struct __user_cap_header_struct hdr = {_LINUX_CAPABILITY_VERSION_3, 0};
    struct __user_cap_data_struct data[2];
    memset(data, 0, sizeof(data));
    if (syscall(SYS_capget, &hdr, data) != 0) {
        perror("escama-launch: capget");
        return 1;
    }
    if ((data[0].permitted & ESCAMA_CAPS) != ESCAMA_CAPS) {
        fprintf(stderr,
                "escama-launch: este binario no tiene las capabilities "
                "necesarias (permitted=0x%x, faltan=0x%x).\n"
                "Reinstalalo con: sudo install.sh install\n"
                "Si getcap las muestra y esto falla, casi seguro:\n"
                "  - el binario es de root y no tuyo (el kernel las descarta), o\n"
                "  - chown AFTER setcap (chown borra la xattr), o\n"
                "  - esta en tmpfs (tmpfs no aplica file capabilities).\n",
                data[0].permitted, ESCAMA_CAPS & ~data[0].permitted);
        return 1;
    }
    data[0].inheritable |= ESCAMA_CAPS;
    if (syscall(SYS_capset, &hdr, data) != 0) {
        perror("escama-launch: capset (sumar al inheritable)");
        return 1;
    }

    /* 2) elevarlas a ambient: sobreviven al execve del nucleo */
    for (unsigned i = 0; i < sizeof(escama_cap_list) / sizeof(*escama_cap_list);
         i++) {
        if (prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_RAISE, escama_cap_list[i], 0,
                  0) != 0) {
            fprintf(stderr, "escama-launch: PR_CAP_AMBIENT_RAISE(%d): %s\n",
                    escama_cap_list[i], strerror(errno));
            return 1;
        }
    }

    /* 3) ejecutar el nucleo. No hay privilege escalation al execve: el archivo
     *    destino no tiene file capabilities, asi que el ambient se conserva.
     *
     *    Modo "core": el propio nucleo se re-ejecuta a traves del launcher para
     *    operar sin sudo (spec `uso-sin-privilegios`). Se ejecuta el interprete
     *    con ruta ABSOLUTA: al re-ejecutarse, el PATH puede no estar disponible
     *    (medido: "execv: No such file or directory" sin esto). */
    if (argc >= 3 && strcmp(argv[1], "core") == 0) {
        char *const py[] = {(char *)ESCAMA_PYTHON, (char *)ESCAMA_CORE, NULL};
        char **nuevo = calloc((size_t)argc + 1, sizeof(char *));
        if (!nuevo) { perror("escama-launch: calloc"); return 1; }
        nuevo[0] = py[0];
        nuevo[1] = py[1];
        for (int i = 2; i < argc; i++)
            nuevo[i] = argv[i];
        nuevo[argc] = NULL;  /* el ultimo arg (argv[argc-1]) queda en su lugar */
        if (setenv("PATH", "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:"
                         "/sbin:/bin", 1) != 0) {
            perror("escama-launch: setenv PATH");
            return 1;
        }
        execv(ESCAMA_PYTHON, nuevo);
        perror("escama-launch: execv python");
        return 127;
    }

    execv(argv[1], &argv[1]);
    perror("escama-launch: execv");
    return 127;
}
