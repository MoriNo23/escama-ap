#!/usr/bin/env python3
"""
escama.py - Núcleo del AP casero "escama" (hostapd + dnsmasq).

Única fuente de lógica. Lee /etc/escama/escama.env como fuente de verdad,
genera hostapd-escama.conf y dnsmasq-escama.conf desde el env, levanta/baja
el AP, valida de verdad (type AP, no grep ssid), y aplica masquerade dinámico
usando WAN_IFACE del env (nunca hardcodeado).

Regla de oro: la iface WAN (stonepi por defecto) SOLO se lee, NUNCA se modifica
(ip addr del, nmcli, hostapd) salvo que el env diga lo contrario.

Uso: sudo escama.py {start|stop|restart|status|reconnect|genconfig}
"""
import os
import sys
import syslog
import subprocess
import shutil
import time
import re

# --- Paths ---
CONFIG_DIR = "/etc/escama"
ENV_FILE = os.path.join(CONFIG_DIR, "escama.env")
HOSTAPD_CONF = "/etc/hostapd/hostapd-escama.conf"
DNSMASQ_CONF = "/etc/dnsmasq-escama.conf"
LOG = "/var/log/escama-ap.log"
LEASE_FILE = "/var/lib/misc/dnsmasq-escama.leases"
PIDFILE = "/run/dnsmasq-escama.pid"

# Defaults (overriden by env)
DEFAULTS = {
    "AP_IFACE": "wn8200nd",
    "WAN_IFACE": "stonepi",
    "SSID": "escama",
    "CHANNEL": "6",
    "HW_MODE": "g",
    "AP_IP": "10.42.1.1",
    "AP_CIDR": "24",
    "AP_SUBNET": "10.42.1.0/24",
    "DHCP_START": "10.42.1.10",
    "DHCP_END": "10.42.1.254",
    "DHCP_LEASE": "12h",
    "WPA_PASSPHRASE": "#GoticasCulonas@@",
    "DNS1": "8.8.8.8",
    "DNS2": "8.8.4.4",
}


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_log__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_log__mutmut)
def log(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_orig(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_1(msg: str) -> None:
    line = None
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_2(msg: str) -> None:
    line = f"{time.strftime(None)} {msg}"
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_3(msg: str) -> None:
    line = f"{time.strftime('XX%H:%M:%SXX')} {msg}"
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_4(msg: str) -> None:
    line = f"{time.strftime('%h:%m:%s')} {msg}"
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_5(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(None, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_6(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(LOG, None) as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_7(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open("a") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_8(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(LOG, ) as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_9(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(LOG, "XXaXX") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_10(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(LOG, "A") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_11(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(LOG, "a") as f:
            f.write(None)
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_12(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(LOG, "a") as f:
            f.write(line - "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_13(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(LOG, "a") as f:
            f.write(line + "XX\nXX")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_14(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(None)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def x_log__mutmut_15(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(None, msg)
    except Exception:
        pass


def x_log__mutmut_16(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, None)
    except Exception:
        pass


def x_log__mutmut_17(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(msg)
    except Exception:
        pass


def x_log__mutmut_18(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, )
    except Exception:
        pass

mutants_x_log__mutmut['_mutmut_orig'] = x_log__mutmut_orig # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_1'] = x_log__mutmut_1 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_2'] = x_log__mutmut_2 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_3'] = x_log__mutmut_3 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_4'] = x_log__mutmut_4 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_5'] = x_log__mutmut_5 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_6'] = x_log__mutmut_6 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_7'] = x_log__mutmut_7 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_8'] = x_log__mutmut_8 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_9'] = x_log__mutmut_9 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_10'] = x_log__mutmut_10 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_11'] = x_log__mutmut_11 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_12'] = x_log__mutmut_12 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_13'] = x_log__mutmut_13 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_14'] = x_log__mutmut_14 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_15'] = x_log__mutmut_15 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_16'] = x_log__mutmut_16 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_17'] = x_log__mutmut_17 # type: ignore # mutmut generated
mutants_x_log__mutmut['x_log__mutmut_18'] = x_log__mutmut_18 # type: ignore # mutmut generated
mutants_x_run__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_run__mutmut)
def run(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_orig(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_1(cmd, check=False, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_2(cmd, check=True, capture=False):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_3(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() == 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_4(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 1:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_5(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = None
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_6(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] - cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_7(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["XXsudoXX"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_8(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["SUDO"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_9(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(None, capture_output=True, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_10(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=None, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_11(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=None)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_12(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(capture_output=True, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_13(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_14(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, )
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_15(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=False, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_16(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=False)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def x_run__mutmut_17(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=True)
        return subprocess.run(None)
    except FileNotFoundError as e:
        if check:
            raise
        return None

mutants_x_run__mutmut['_mutmut_orig'] = x_run__mutmut_orig # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_1'] = x_run__mutmut_1 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_2'] = x_run__mutmut_2 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_3'] = x_run__mutmut_3 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_4'] = x_run__mutmut_4 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_5'] = x_run__mutmut_5 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_6'] = x_run__mutmut_6 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_7'] = x_run__mutmut_7 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_8'] = x_run__mutmut_8 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_9'] = x_run__mutmut_9 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_10'] = x_run__mutmut_10 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_11'] = x_run__mutmut_11 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_12'] = x_run__mutmut_12 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_13'] = x_run__mutmut_13 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_14'] = x_run__mutmut_14 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_15'] = x_run__mutmut_15 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_16'] = x_run__mutmut_16 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_17'] = x_run__mutmut_17 # type: ignore # mutmut generated
mutants_x_load_env__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_load_env__mutmut)
def load_env() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_orig() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_1() -> dict:
    cfg = None
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_2() -> dict:
    cfg = dict(None)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_3() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(None):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_4() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(None) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_5() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = None
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_6() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") and "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_7() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line and line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_8() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_9() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(None) or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_10() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("XX#XX") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_11() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "XX=XX" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_12() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_13() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    break
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_14() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = None
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_15() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split(None, 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_16() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", None)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_17() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split(1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_18() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", )
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_19() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.rsplit("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_20() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("XX=XX", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_21() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 2)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def x_load_env__mutmut_22() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = None
    return cfg


def x_load_env__mutmut_23() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip(None)
    return cfg


def x_load_env__mutmut_24() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip(None).strip("'")
    return cfg


def x_load_env__mutmut_25() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('XX"XX').strip("'")
    return cfg


def x_load_env__mutmut_26() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("XX'XX")
    return cfg

mutants_x_load_env__mutmut['_mutmut_orig'] = x_load_env__mutmut_orig # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_1'] = x_load_env__mutmut_1 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_2'] = x_load_env__mutmut_2 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_3'] = x_load_env__mutmut_3 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_4'] = x_load_env__mutmut_4 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_5'] = x_load_env__mutmut_5 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_6'] = x_load_env__mutmut_6 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_7'] = x_load_env__mutmut_7 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_8'] = x_load_env__mutmut_8 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_9'] = x_load_env__mutmut_9 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_10'] = x_load_env__mutmut_10 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_11'] = x_load_env__mutmut_11 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_12'] = x_load_env__mutmut_12 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_13'] = x_load_env__mutmut_13 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_14'] = x_load_env__mutmut_14 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_15'] = x_load_env__mutmut_15 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_16'] = x_load_env__mutmut_16 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_17'] = x_load_env__mutmut_17 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_18'] = x_load_env__mutmut_18 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_19'] = x_load_env__mutmut_19 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_20'] = x_load_env__mutmut_20 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_21'] = x_load_env__mutmut_21 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_22'] = x_load_env__mutmut_22 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_23'] = x_load_env__mutmut_23 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_24'] = x_load_env__mutmut_24 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_25'] = x_load_env__mutmut_25 # type: ignore # mutmut generated
mutants_x_load_env__mutmut['x_load_env__mutmut_26'] = x_load_env__mutmut_26 # type: ignore # mutmut generated
mutants_x_iface_exists__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_iface_exists__mutmut)
def iface_exists(iface: str) -> bool:
    return os.path.islink(f"/sys/class/net/{iface}")


def x_iface_exists__mutmut_orig(iface: str) -> bool:
    return os.path.islink(f"/sys/class/net/{iface}")


def x_iface_exists__mutmut_1(iface: str) -> bool:
    return os.path.islink(None)

mutants_x_iface_exists__mutmut['_mutmut_orig'] = x_iface_exists__mutmut_orig # type: ignore # mutmut generated
mutants_x_iface_exists__mutmut['x_iface_exists__mutmut_1'] = x_iface_exists__mutmut_1 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_wan_has_internet__mutmut)
def wan_has_internet(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_orig(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_1(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = None
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_2(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(None, capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_3(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=None)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_4(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_5(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], )
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_6(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["XXipXX", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_7(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["IP", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_8(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "XXrouteXX", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_9(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "ROUTE", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_10(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "XXshowXX", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_11(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "SHOW", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_12(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "XXdevXX", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_13(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "DEV", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_14(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=False)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_15(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = ""
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_16(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout and "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_17(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "XXXX").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_18(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "XXdefaultXX" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_19(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "DEFAULT" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_20(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" not in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_21(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = None
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_22(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(None, l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_23(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", None)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_24(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_25(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", )
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_26(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"XXvia (\S+)XX", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_27(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"VIA (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_28(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = None
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_29(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(None)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_30(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(2)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_31(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                return
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_32(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_33(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return True
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_34(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = None
    return p.returncode == 0


def x_wan_has_internet__mutmut_35(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(None, capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_36(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=None)
    return p.returncode == 0


def x_wan_has_internet__mutmut_37(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_38(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], )
    return p.returncode == 0


def x_wan_has_internet__mutmut_39(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["XXpingXX", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_40(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["PING", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_41(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "XX-cXX", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_42(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-C", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_43(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "XX1XX", "-W", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_44(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "XX-WXX", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_45(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-w", "3", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_46(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "XX3XX", gw], capture=True)
    return p.returncode == 0


def x_wan_has_internet__mutmut_47(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=False)
    return p.returncode == 0


def x_wan_has_internet__mutmut_48(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode != 0


def x_wan_has_internet__mutmut_49(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 1

mutants_x_wan_has_internet__mutmut['_mutmut_orig'] = x_wan_has_internet__mutmut_orig # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_1'] = x_wan_has_internet__mutmut_1 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_2'] = x_wan_has_internet__mutmut_2 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_3'] = x_wan_has_internet__mutmut_3 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_4'] = x_wan_has_internet__mutmut_4 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_5'] = x_wan_has_internet__mutmut_5 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_6'] = x_wan_has_internet__mutmut_6 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_7'] = x_wan_has_internet__mutmut_7 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_8'] = x_wan_has_internet__mutmut_8 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_9'] = x_wan_has_internet__mutmut_9 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_10'] = x_wan_has_internet__mutmut_10 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_11'] = x_wan_has_internet__mutmut_11 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_12'] = x_wan_has_internet__mutmut_12 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_13'] = x_wan_has_internet__mutmut_13 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_14'] = x_wan_has_internet__mutmut_14 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_15'] = x_wan_has_internet__mutmut_15 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_16'] = x_wan_has_internet__mutmut_16 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_17'] = x_wan_has_internet__mutmut_17 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_18'] = x_wan_has_internet__mutmut_18 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_19'] = x_wan_has_internet__mutmut_19 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_20'] = x_wan_has_internet__mutmut_20 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_21'] = x_wan_has_internet__mutmut_21 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_22'] = x_wan_has_internet__mutmut_22 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_23'] = x_wan_has_internet__mutmut_23 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_24'] = x_wan_has_internet__mutmut_24 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_25'] = x_wan_has_internet__mutmut_25 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_26'] = x_wan_has_internet__mutmut_26 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_27'] = x_wan_has_internet__mutmut_27 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_28'] = x_wan_has_internet__mutmut_28 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_29'] = x_wan_has_internet__mutmut_29 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_30'] = x_wan_has_internet__mutmut_30 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_31'] = x_wan_has_internet__mutmut_31 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_32'] = x_wan_has_internet__mutmut_32 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_33'] = x_wan_has_internet__mutmut_33 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_34'] = x_wan_has_internet__mutmut_34 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_35'] = x_wan_has_internet__mutmut_35 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_36'] = x_wan_has_internet__mutmut_36 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_37'] = x_wan_has_internet__mutmut_37 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_38'] = x_wan_has_internet__mutmut_38 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_39'] = x_wan_has_internet__mutmut_39 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_40'] = x_wan_has_internet__mutmut_40 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_41'] = x_wan_has_internet__mutmut_41 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_42'] = x_wan_has_internet__mutmut_42 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_43'] = x_wan_has_internet__mutmut_43 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_44'] = x_wan_has_internet__mutmut_44 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_45'] = x_wan_has_internet__mutmut_45 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_46'] = x_wan_has_internet__mutmut_46 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_47'] = x_wan_has_internet__mutmut_47 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_48'] = x_wan_has_internet__mutmut_48 # type: ignore # mutmut generated
mutants_x_wan_has_internet__mutmut['x_wan_has_internet__mutmut_49'] = x_wan_has_internet__mutmut_49 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_module_has_ap_mode__mutmut)
def module_has_ap_mode() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_orig() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_1() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = None
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_2() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(None, capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_3() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=None)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_4() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_5() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], )
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_6() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["XXiwXX", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_7() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["IW", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_8() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "XXphyXX", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_9() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "PHY", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_10() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "XXinfoXX"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_11() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "INFO"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_12() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=False)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_13() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode == 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_14() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 1:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_15() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return True
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_16() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") and "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_17() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "XXtype APXX" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_18() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type ap" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_19() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "TYPE AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_20() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" not in (p.stdout or "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_21() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout and "") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_22() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "XXXX") or "* AP" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_23() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "XX* APXX" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_24() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* ap" in (p.stdout or "")


def x_module_has_ap_mode__mutmut_25() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" not in (p.stdout or "")


def x_module_has_ap_mode__mutmut_26() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout and "")


def x_module_has_ap_mode__mutmut_27() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "XXXX")

mutants_x_module_has_ap_mode__mutmut['_mutmut_orig'] = x_module_has_ap_mode__mutmut_orig # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_1'] = x_module_has_ap_mode__mutmut_1 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_2'] = x_module_has_ap_mode__mutmut_2 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_3'] = x_module_has_ap_mode__mutmut_3 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_4'] = x_module_has_ap_mode__mutmut_4 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_5'] = x_module_has_ap_mode__mutmut_5 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_6'] = x_module_has_ap_mode__mutmut_6 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_7'] = x_module_has_ap_mode__mutmut_7 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_8'] = x_module_has_ap_mode__mutmut_8 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_9'] = x_module_has_ap_mode__mutmut_9 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_10'] = x_module_has_ap_mode__mutmut_10 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_11'] = x_module_has_ap_mode__mutmut_11 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_12'] = x_module_has_ap_mode__mutmut_12 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_13'] = x_module_has_ap_mode__mutmut_13 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_14'] = x_module_has_ap_mode__mutmut_14 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_15'] = x_module_has_ap_mode__mutmut_15 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_16'] = x_module_has_ap_mode__mutmut_16 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_17'] = x_module_has_ap_mode__mutmut_17 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_18'] = x_module_has_ap_mode__mutmut_18 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_19'] = x_module_has_ap_mode__mutmut_19 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_20'] = x_module_has_ap_mode__mutmut_20 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_21'] = x_module_has_ap_mode__mutmut_21 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_22'] = x_module_has_ap_mode__mutmut_22 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_23'] = x_module_has_ap_mode__mutmut_23 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_24'] = x_module_has_ap_mode__mutmut_24 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_25'] = x_module_has_ap_mode__mutmut_25 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_26'] = x_module_has_ap_mode__mutmut_26 # type: ignore # mutmut generated
mutants_x_module_has_ap_mode__mutmut['x_module_has_ap_mode__mutmut_27'] = x_module_has_ap_mode__mutmut_27 # type: ignore # mutmut generated
mutants_x__ap_phy__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__ap_phy__mutmut)
def _ap_phy() -> str:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    phy = f"/sys/class/net/{ap}/phy80211"
    if os.path.islink(phy):
        return os.path.basename(os.readlink(phy))
    return ""


def x__ap_phy__mutmut_orig() -> str:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    phy = f"/sys/class/net/{ap}/phy80211"
    if os.path.islink(phy):
        return os.path.basename(os.readlink(phy))
    return ""


def x__ap_phy__mutmut_1() -> str:
    cfg = None
    ap = cfg["AP_IFACE"]
    phy = f"/sys/class/net/{ap}/phy80211"
    if os.path.islink(phy):
        return os.path.basename(os.readlink(phy))
    return ""


def x__ap_phy__mutmut_2() -> str:
    cfg = load_env()
    ap = None
    phy = f"/sys/class/net/{ap}/phy80211"
    if os.path.islink(phy):
        return os.path.basename(os.readlink(phy))
    return ""


def x__ap_phy__mutmut_3() -> str:
    cfg = load_env()
    ap = cfg["XXAP_IFACEXX"]
    phy = f"/sys/class/net/{ap}/phy80211"
    if os.path.islink(phy):
        return os.path.basename(os.readlink(phy))
    return ""


def x__ap_phy__mutmut_4() -> str:
    cfg = load_env()
    ap = cfg["ap_iface"]
    phy = f"/sys/class/net/{ap}/phy80211"
    if os.path.islink(phy):
        return os.path.basename(os.readlink(phy))
    return ""


def x__ap_phy__mutmut_5() -> str:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    phy = None
    if os.path.islink(phy):
        return os.path.basename(os.readlink(phy))
    return ""


def x__ap_phy__mutmut_6() -> str:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    phy = f"/sys/class/net/{ap}/phy80211"
    if os.path.islink(None):
        return os.path.basename(os.readlink(phy))
    return ""


def x__ap_phy__mutmut_7() -> str:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    phy = f"/sys/class/net/{ap}/phy80211"
    if os.path.islink(phy):
        return os.path.basename(None)
    return ""


def x__ap_phy__mutmut_8() -> str:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    phy = f"/sys/class/net/{ap}/phy80211"
    if os.path.islink(phy):
        return os.path.basename(os.readlink(None))
    return ""


def x__ap_phy__mutmut_9() -> str:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    phy = f"/sys/class/net/{ap}/phy80211"
    if os.path.islink(phy):
        return os.path.basename(os.readlink(phy))
    return "XXXX"

mutants_x__ap_phy__mutmut['_mutmut_orig'] = x__ap_phy__mutmut_orig # type: ignore # mutmut generated
mutants_x__ap_phy__mutmut['x__ap_phy__mutmut_1'] = x__ap_phy__mutmut_1 # type: ignore # mutmut generated
mutants_x__ap_phy__mutmut['x__ap_phy__mutmut_2'] = x__ap_phy__mutmut_2 # type: ignore # mutmut generated
mutants_x__ap_phy__mutmut['x__ap_phy__mutmut_3'] = x__ap_phy__mutmut_3 # type: ignore # mutmut generated
mutants_x__ap_phy__mutmut['x__ap_phy__mutmut_4'] = x__ap_phy__mutmut_4 # type: ignore # mutmut generated
mutants_x__ap_phy__mutmut['x__ap_phy__mutmut_5'] = x__ap_phy__mutmut_5 # type: ignore # mutmut generated
mutants_x__ap_phy__mutmut['x__ap_phy__mutmut_6'] = x__ap_phy__mutmut_6 # type: ignore # mutmut generated
mutants_x__ap_phy__mutmut['x__ap_phy__mutmut_7'] = x__ap_phy__mutmut_7 # type: ignore # mutmut generated
mutants_x__ap_phy__mutmut['x__ap_phy__mutmut_8'] = x__ap_phy__mutmut_8 # type: ignore # mutmut generated
mutants_x__ap_phy__mutmut['x__ap_phy__mutmut_9'] = x__ap_phy__mutmut_9 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_reload_module_if_needed__mutmut)
def reload_module_if_needed(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_orig(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_1(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_2(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(None):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_3(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = None
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_4(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_5(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = None
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_6(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(None, capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_7(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=None)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_8(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_9(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], )
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_10(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["XXiwXX", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_11(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["IW", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_12(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "XXphyXX", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_13(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "PHY", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_14(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "XXinfoXX"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_15(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "INFO"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_16(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=False)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_17(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 or "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_18(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode != 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_19(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 1 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_20(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "XX* APXX" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_21(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* ap" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_22(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_23(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout and ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_24(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or "XXXX"):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_25(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(None)
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_26(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(None, check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_27(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=None)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_28(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_29(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], )
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_30(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["XXrmmodXX", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_31(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["RMMOD", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_32(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "XX8192euXX"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_33(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192EU"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_34(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=True)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_35(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(None)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_36(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(2)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_37(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(None, check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_38(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=None)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_39(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_40(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], )
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_41(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["XXdepmodXX", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_42(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["DEPMOD", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_43(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "XX-aXX"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_44(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-A"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_45(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=True)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_46(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(None, check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_47(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=None)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_48(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_49(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], )
        time.sleep(2)


def x_reload_module_if_needed__mutmut_50(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["XXmodprobeXX", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_51(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["MODPROBE", "8192eu"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_52(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "XX8192euXX"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_53(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192EU"], check=False)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_54(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=True)
        time.sleep(2)


def x_reload_module_if_needed__mutmut_55(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(None)


def x_reload_module_if_needed__mutmut_56(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(3)

mutants_x_reload_module_if_needed__mutmut['_mutmut_orig'] = x_reload_module_if_needed__mutmut_orig # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_1'] = x_reload_module_if_needed__mutmut_1 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_2'] = x_reload_module_if_needed__mutmut_2 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_3'] = x_reload_module_if_needed__mutmut_3 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_4'] = x_reload_module_if_needed__mutmut_4 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_5'] = x_reload_module_if_needed__mutmut_5 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_6'] = x_reload_module_if_needed__mutmut_6 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_7'] = x_reload_module_if_needed__mutmut_7 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_8'] = x_reload_module_if_needed__mutmut_8 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_9'] = x_reload_module_if_needed__mutmut_9 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_10'] = x_reload_module_if_needed__mutmut_10 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_11'] = x_reload_module_if_needed__mutmut_11 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_12'] = x_reload_module_if_needed__mutmut_12 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_13'] = x_reload_module_if_needed__mutmut_13 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_14'] = x_reload_module_if_needed__mutmut_14 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_15'] = x_reload_module_if_needed__mutmut_15 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_16'] = x_reload_module_if_needed__mutmut_16 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_17'] = x_reload_module_if_needed__mutmut_17 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_18'] = x_reload_module_if_needed__mutmut_18 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_19'] = x_reload_module_if_needed__mutmut_19 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_20'] = x_reload_module_if_needed__mutmut_20 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_21'] = x_reload_module_if_needed__mutmut_21 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_22'] = x_reload_module_if_needed__mutmut_22 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_23'] = x_reload_module_if_needed__mutmut_23 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_24'] = x_reload_module_if_needed__mutmut_24 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_25'] = x_reload_module_if_needed__mutmut_25 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_26'] = x_reload_module_if_needed__mutmut_26 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_27'] = x_reload_module_if_needed__mutmut_27 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_28'] = x_reload_module_if_needed__mutmut_28 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_29'] = x_reload_module_if_needed__mutmut_29 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_30'] = x_reload_module_if_needed__mutmut_30 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_31'] = x_reload_module_if_needed__mutmut_31 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_32'] = x_reload_module_if_needed__mutmut_32 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_33'] = x_reload_module_if_needed__mutmut_33 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_34'] = x_reload_module_if_needed__mutmut_34 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_35'] = x_reload_module_if_needed__mutmut_35 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_36'] = x_reload_module_if_needed__mutmut_36 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_37'] = x_reload_module_if_needed__mutmut_37 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_38'] = x_reload_module_if_needed__mutmut_38 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_39'] = x_reload_module_if_needed__mutmut_39 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_40'] = x_reload_module_if_needed__mutmut_40 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_41'] = x_reload_module_if_needed__mutmut_41 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_42'] = x_reload_module_if_needed__mutmut_42 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_43'] = x_reload_module_if_needed__mutmut_43 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_44'] = x_reload_module_if_needed__mutmut_44 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_45'] = x_reload_module_if_needed__mutmut_45 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_46'] = x_reload_module_if_needed__mutmut_46 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_47'] = x_reload_module_if_needed__mutmut_47 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_48'] = x_reload_module_if_needed__mutmut_48 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_49'] = x_reload_module_if_needed__mutmut_49 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_50'] = x_reload_module_if_needed__mutmut_50 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_51'] = x_reload_module_if_needed__mutmut_51 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_52'] = x_reload_module_if_needed__mutmut_52 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_53'] = x_reload_module_if_needed__mutmut_53 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_54'] = x_reload_module_if_needed__mutmut_54 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_55'] = x_reload_module_if_needed__mutmut_55 # type: ignore # mutmut generated
mutants_x_reload_module_if_needed__mutmut['x_reload_module_if_needed__mutmut_56'] = x_reload_module_if_needed__mutmut_56 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_generate_configs__mutmut)
def generate_configs(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_orig(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_1(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = None
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_2(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['XXAP_IFACEXX']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_3(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['ap_iface']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_4(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['XXSSIDXX']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_5(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['ssid']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_6(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['XXHW_MODEXX']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_7(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['hw_mode']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_8(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['XXCHANNELXX']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_9(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['channel']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_10(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['XXWPA_PASSPHRASEXX']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_11(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['wpa_passphrase']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_12(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = None
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_13(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['XXAP_IFACEXX']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_14(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['ap_iface']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_15(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['XXDHCP_STARTXX']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_16(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['dhcp_start']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_17(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['XXDHCP_ENDXX']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_18(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['dhcp_end']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_19(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['XXDHCP_LEASEXX']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_20(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['dhcp_lease']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_21(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['XXAP_IPXX']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_22(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['ap_ip']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_23(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['XXDNS1XX']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_24(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['dns1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_25(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['XXDNS2XX']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_26(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['dns2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_27(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(None, exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_28(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=None)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_29(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_30(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), )
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_31(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(None), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_32(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=False)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_33(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(None, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_34(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, None) as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_35(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open("w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_36(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, ) as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_37(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "XXwXX") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_38(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "W") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_39(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(None)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_40(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(None, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_41(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, None) as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_42(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open("w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_43(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, ) as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_44(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "XXwXX") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_45(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "W") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_46(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(None)
    log("Configs regenerated from escama.env")


def x_generate_configs__mutmut_47(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log(None)


def x_generate_configs__mutmut_48(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("XXConfigs regenerated from escama.envXX")


def x_generate_configs__mutmut_49(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("configs regenerated from escama.env")


def x_generate_configs__mutmut_50(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("CONFIGS REGENERATED FROM ESCAMA.ENV")

mutants_x_generate_configs__mutmut['_mutmut_orig'] = x_generate_configs__mutmut_orig # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_1'] = x_generate_configs__mutmut_1 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_2'] = x_generate_configs__mutmut_2 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_3'] = x_generate_configs__mutmut_3 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_4'] = x_generate_configs__mutmut_4 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_5'] = x_generate_configs__mutmut_5 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_6'] = x_generate_configs__mutmut_6 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_7'] = x_generate_configs__mutmut_7 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_8'] = x_generate_configs__mutmut_8 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_9'] = x_generate_configs__mutmut_9 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_10'] = x_generate_configs__mutmut_10 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_11'] = x_generate_configs__mutmut_11 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_12'] = x_generate_configs__mutmut_12 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_13'] = x_generate_configs__mutmut_13 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_14'] = x_generate_configs__mutmut_14 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_15'] = x_generate_configs__mutmut_15 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_16'] = x_generate_configs__mutmut_16 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_17'] = x_generate_configs__mutmut_17 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_18'] = x_generate_configs__mutmut_18 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_19'] = x_generate_configs__mutmut_19 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_20'] = x_generate_configs__mutmut_20 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_21'] = x_generate_configs__mutmut_21 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_22'] = x_generate_configs__mutmut_22 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_23'] = x_generate_configs__mutmut_23 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_24'] = x_generate_configs__mutmut_24 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_25'] = x_generate_configs__mutmut_25 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_26'] = x_generate_configs__mutmut_26 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_27'] = x_generate_configs__mutmut_27 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_28'] = x_generate_configs__mutmut_28 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_29'] = x_generate_configs__mutmut_29 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_30'] = x_generate_configs__mutmut_30 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_31'] = x_generate_configs__mutmut_31 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_32'] = x_generate_configs__mutmut_32 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_33'] = x_generate_configs__mutmut_33 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_34'] = x_generate_configs__mutmut_34 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_35'] = x_generate_configs__mutmut_35 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_36'] = x_generate_configs__mutmut_36 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_37'] = x_generate_configs__mutmut_37 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_38'] = x_generate_configs__mutmut_38 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_39'] = x_generate_configs__mutmut_39 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_40'] = x_generate_configs__mutmut_40 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_41'] = x_generate_configs__mutmut_41 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_42'] = x_generate_configs__mutmut_42 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_43'] = x_generate_configs__mutmut_43 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_44'] = x_generate_configs__mutmut_44 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_45'] = x_generate_configs__mutmut_45 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_46'] = x_generate_configs__mutmut_46 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_47'] = x_generate_configs__mutmut_47 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_48'] = x_generate_configs__mutmut_48 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_49'] = x_generate_configs__mutmut_49 # type: ignore # mutmut generated
mutants_x_generate_configs__mutmut['x_generate_configs__mutmut_50'] = x_generate_configs__mutmut_50 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__kill_procs__mutmut)
def _kill_procs() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_orig() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_1() -> None:
    run(None, check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_2() -> None:
    run(["pkill", "-x", "hostapd"], check=None)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_3() -> None:
    run(check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_4() -> None:
    run(["pkill", "-x", "hostapd"], )
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_5() -> None:
    run(["XXpkillXX", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_6() -> None:
    run(["PKILL", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_7() -> None:
    run(["pkill", "XX-xXX", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_8() -> None:
    run(["pkill", "-X", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_9() -> None:
    run(["pkill", "-x", "XXhostapdXX"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_10() -> None:
    run(["pkill", "-x", "HOSTAPD"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_11() -> None:
    run(["pkill", "-x", "hostapd"], check=True)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_12() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(None, check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_13() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=None)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_14() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_15() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], )
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_16() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["XXpkillXX", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_17() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["PKILL", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_18() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "XX-xXX", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_19() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-X", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_20() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "XXdnsmasqXX"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_21() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "DNSMASQ"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_22() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=True)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_23() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(None)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_24() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(2)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_25() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(None, check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_26() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=None)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_27() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_28() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], )
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_29() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["XXpkillXX", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_30() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["PKILL", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_31() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "XX-9XX", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_32() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "XX-xXX", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_33() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-X", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_34() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "XXhostapdXX"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_35() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "HOSTAPD"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_36() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=True)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_37() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(None, check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_38() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=None)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_39() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_40() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], )
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_41() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["XXpkillXX", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_42() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["PKILL", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_43() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "XX-9XX", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_44() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "XX-xXX", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_45() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-X", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_46() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "XXdnsmasqXX"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_47() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "DNSMASQ"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_48() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=True)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_49() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(None):
        os.remove(PIDFILE)


def x__kill_procs__mutmut_50() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(None)

mutants_x__kill_procs__mutmut['_mutmut_orig'] = x__kill_procs__mutmut_orig # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_1'] = x__kill_procs__mutmut_1 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_2'] = x__kill_procs__mutmut_2 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_3'] = x__kill_procs__mutmut_3 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_4'] = x__kill_procs__mutmut_4 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_5'] = x__kill_procs__mutmut_5 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_6'] = x__kill_procs__mutmut_6 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_7'] = x__kill_procs__mutmut_7 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_8'] = x__kill_procs__mutmut_8 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_9'] = x__kill_procs__mutmut_9 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_10'] = x__kill_procs__mutmut_10 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_11'] = x__kill_procs__mutmut_11 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_12'] = x__kill_procs__mutmut_12 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_13'] = x__kill_procs__mutmut_13 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_14'] = x__kill_procs__mutmut_14 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_15'] = x__kill_procs__mutmut_15 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_16'] = x__kill_procs__mutmut_16 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_17'] = x__kill_procs__mutmut_17 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_18'] = x__kill_procs__mutmut_18 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_19'] = x__kill_procs__mutmut_19 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_20'] = x__kill_procs__mutmut_20 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_21'] = x__kill_procs__mutmut_21 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_22'] = x__kill_procs__mutmut_22 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_23'] = x__kill_procs__mutmut_23 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_24'] = x__kill_procs__mutmut_24 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_25'] = x__kill_procs__mutmut_25 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_26'] = x__kill_procs__mutmut_26 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_27'] = x__kill_procs__mutmut_27 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_28'] = x__kill_procs__mutmut_28 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_29'] = x__kill_procs__mutmut_29 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_30'] = x__kill_procs__mutmut_30 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_31'] = x__kill_procs__mutmut_31 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_32'] = x__kill_procs__mutmut_32 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_33'] = x__kill_procs__mutmut_33 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_34'] = x__kill_procs__mutmut_34 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_35'] = x__kill_procs__mutmut_35 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_36'] = x__kill_procs__mutmut_36 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_37'] = x__kill_procs__mutmut_37 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_38'] = x__kill_procs__mutmut_38 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_39'] = x__kill_procs__mutmut_39 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_40'] = x__kill_procs__mutmut_40 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_41'] = x__kill_procs__mutmut_41 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_42'] = x__kill_procs__mutmut_42 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_43'] = x__kill_procs__mutmut_43 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_44'] = x__kill_procs__mutmut_44 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_45'] = x__kill_procs__mutmut_45 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_46'] = x__kill_procs__mutmut_46 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_47'] = x__kill_procs__mutmut_47 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_48'] = x__kill_procs__mutmut_48 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_49'] = x__kill_procs__mutmut_49 # type: ignore # mutmut generated
mutants_x__kill_procs__mutmut['x__kill_procs__mutmut_50'] = x__kill_procs__mutmut_50 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__ensure_ip__mutmut)
def _ensure_ip(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_orig(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_1(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(None, check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_2(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=None)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_3(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_4(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], )
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_5(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["XXipXX", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_6(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["IP", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_7(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "XXaddrXX", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_8(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "ADDR", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_9(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "XXflushXX", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_10(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "FLUSH", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_11(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "XXdevXX", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_12(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "DEV", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_13(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=True)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_14(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(None, check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_15(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=None)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_16(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_17(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], )
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_18(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["XXipXX", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_19(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["IP", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_20(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "XXlinkXX", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_21(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "LINK", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_22(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "XXsetXX", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_23(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "SET", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_24(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "XXdownXX"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_25(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "DOWN"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_26(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=True)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_27(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(None)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_28(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(2)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_29(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(None, check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_30(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=None)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_31(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_32(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], )
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_33(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["XXipXX", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_34(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["IP", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_35(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "XXlinkXX", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_36(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "LINK", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_37(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "XXsetXX", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_38(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "SET", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_39(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "XXupXX"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_40(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "UP"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_41(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=True)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_42(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(None, check=False)


def x__ensure_ip__mutmut_43(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=None)


def x__ensure_ip__mutmut_44(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(check=False)


def x__ensure_ip__mutmut_45(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], )


def x__ensure_ip__mutmut_46(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["XXipXX", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_47(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["IP", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_48(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "XXaddrXX", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_49(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "ADDR", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_50(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "XXaddXX", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_51(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "ADD", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def x__ensure_ip__mutmut_52(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "XXdevXX", ap], check=False)


def x__ensure_ip__mutmut_53(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "DEV", ap], check=False)


def x__ensure_ip__mutmut_54(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=True)

mutants_x__ensure_ip__mutmut['_mutmut_orig'] = x__ensure_ip__mutmut_orig # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_1'] = x__ensure_ip__mutmut_1 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_2'] = x__ensure_ip__mutmut_2 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_3'] = x__ensure_ip__mutmut_3 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_4'] = x__ensure_ip__mutmut_4 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_5'] = x__ensure_ip__mutmut_5 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_6'] = x__ensure_ip__mutmut_6 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_7'] = x__ensure_ip__mutmut_7 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_8'] = x__ensure_ip__mutmut_8 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_9'] = x__ensure_ip__mutmut_9 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_10'] = x__ensure_ip__mutmut_10 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_11'] = x__ensure_ip__mutmut_11 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_12'] = x__ensure_ip__mutmut_12 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_13'] = x__ensure_ip__mutmut_13 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_14'] = x__ensure_ip__mutmut_14 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_15'] = x__ensure_ip__mutmut_15 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_16'] = x__ensure_ip__mutmut_16 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_17'] = x__ensure_ip__mutmut_17 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_18'] = x__ensure_ip__mutmut_18 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_19'] = x__ensure_ip__mutmut_19 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_20'] = x__ensure_ip__mutmut_20 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_21'] = x__ensure_ip__mutmut_21 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_22'] = x__ensure_ip__mutmut_22 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_23'] = x__ensure_ip__mutmut_23 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_24'] = x__ensure_ip__mutmut_24 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_25'] = x__ensure_ip__mutmut_25 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_26'] = x__ensure_ip__mutmut_26 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_27'] = x__ensure_ip__mutmut_27 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_28'] = x__ensure_ip__mutmut_28 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_29'] = x__ensure_ip__mutmut_29 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_30'] = x__ensure_ip__mutmut_30 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_31'] = x__ensure_ip__mutmut_31 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_32'] = x__ensure_ip__mutmut_32 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_33'] = x__ensure_ip__mutmut_33 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_34'] = x__ensure_ip__mutmut_34 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_35'] = x__ensure_ip__mutmut_35 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_36'] = x__ensure_ip__mutmut_36 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_37'] = x__ensure_ip__mutmut_37 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_38'] = x__ensure_ip__mutmut_38 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_39'] = x__ensure_ip__mutmut_39 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_40'] = x__ensure_ip__mutmut_40 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_41'] = x__ensure_ip__mutmut_41 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_42'] = x__ensure_ip__mutmut_42 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_43'] = x__ensure_ip__mutmut_43 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_44'] = x__ensure_ip__mutmut_44 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_45'] = x__ensure_ip__mutmut_45 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_46'] = x__ensure_ip__mutmut_46 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_47'] = x__ensure_ip__mutmut_47 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_48'] = x__ensure_ip__mutmut_48 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_49'] = x__ensure_ip__mutmut_49 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_50'] = x__ensure_ip__mutmut_50 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_51'] = x__ensure_ip__mutmut_51 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_52'] = x__ensure_ip__mutmut_52 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_53'] = x__ensure_ip__mutmut_53 # type: ignore # mutmut generated
mutants_x__ensure_ip__mutmut['x__ensure_ip__mutmut_54'] = x__ensure_ip__mutmut_54 # type: ignore # mutmut generated
mutants_x_do_start__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_do_start__mutmut)
def do_start() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_orig() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_1() -> int:
    cfg = None
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_2() -> int:
    cfg = load_env()
    ap = None
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_3() -> int:
    cfg = load_env()
    ap = cfg["XXAP_IFACEXX"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_4() -> int:
    cfg = load_env()
    ap = cfg["ap_iface"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_5() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = None
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_6() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["XXWAN_IFACEXX"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_7() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["wan_iface"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_8() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_9() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = None
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_10() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(None, capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_11() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=None)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_12() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_13() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], )
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_14() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["XXipXX", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_15() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["IP", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_16() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "XXrouteXX", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_17() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "ROUTE", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_18() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "XXshowXX", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_19() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "SHOW", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_20() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "XXdefaultXX"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_21() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "DEFAULT"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_22() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=False)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_23() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout and "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_24() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "XXXX").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_25() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = None
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_26() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(None, l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_27() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", None)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_28() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_29() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", )
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_30() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"XXdev (\S+)XX", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_31() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"DEV (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_32() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = None
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_33() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(None)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_34() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(2)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_35() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                return
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_36() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_37() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = None
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_38() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "XXstonepiXX"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_39() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "STONEPI"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_40() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = None

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_41() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["XXWAN_IFACEXX"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_42() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["wan_iface"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_43() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_44() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(None):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_45() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(None)
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_46() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 2
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_47() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_48() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(None):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_49() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(None)

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_50() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(None, check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_51() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=None)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_52() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_53() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], )
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_54() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["XXnmcliXX", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_55() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["NMCLI", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_56() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "XXdeviceXX", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_57() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "DEVICE", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_58() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "XXsetXX", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_59() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "SET", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_60() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "XXmanagedXX", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_61() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "MANAGED", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_62() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "XXnoXX"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_63() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "NO"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_64() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=True)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_65() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(None)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_66() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(None)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_67() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(None, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_68() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, None, cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_69() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], None)

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_70() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_71() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_72() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], )

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_73() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["XXAP_IPXX"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_74() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["ap_ip"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_75() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["XXAP_CIDRXX"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_76() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["ap_cidr"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_77() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = None
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_78() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(None, check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_79() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=None)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_80() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_81() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], )
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_82() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["XXhostapdXX", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_83() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["HOSTAPD", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_84() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "XX-BXX", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_85() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-b", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_86() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=True)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_87() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode == 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_88() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 1:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_89() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(None)
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_90() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 2
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_91() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(None)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_92() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(4)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_93() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(None, check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_94() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=None)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_95() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_96() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], )

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_97() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["XXdnsmasqXX", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_98() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["DNSMASQ", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_99() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" - DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_100() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "XX--conf-file=XX" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_101() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--CONF-FILE=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_102() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" - PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_103() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "XX--pid-file=XX" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_104() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--PID-FILE=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_105() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=True)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_106() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(None, check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_107() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=None)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_108() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_109() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], )
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_110() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["XXsysctlXX", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_111() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["SYSCTL", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_112() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "XX-wXX", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_113() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-W", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_114() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "XXnet.ipv4.ip_forward=1XX"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_115() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "NET.IPV4.IP_FORWARD=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_116() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=True)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_117() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(None, check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_118() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=None)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_119() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_120() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], )

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_121() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["XXiptablesXX", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_122() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["IPTABLES", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_123() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "XX-tXX", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_124() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-T", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_125() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "XXnatXX", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_126() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "NAT", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_127() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "XX-AXX", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_128() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-a", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_129() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "XXPOSTROUTINGXX",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_130() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "postrouting",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_131() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "XX-oXX", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_132() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-O", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_133() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "XX-sXX", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_134() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-S", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_135() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["XXAP_SUBNETXX"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_136() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["ap_subnet"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_137() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "XX-jXX", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_138() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-J", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_139() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "XXMASQUERADEXX"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_140() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "masquerade"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_141() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=True)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_142() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = None
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_143() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(None, capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_144() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=None)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_145() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_146() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], )
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_147() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["XXiwXX", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_148() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["IW", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_149() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "XXdevXX", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_150() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "DEV", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_151() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "XXinfoXX"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_152() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "INFO"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_153() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=False)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_154() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 or "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_155() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode != 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_156() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 1 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_157() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "XXtype APXX" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_158() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type ap" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_159() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "TYPE AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_160() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" not in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_161() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout and ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_162() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or "XXXX"):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_163() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(None)
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_164() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['XXAP_IPXX']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_165() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['ap_ip']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_166() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['XXAP_CIDRXX']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_167() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['ap_cidr']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_168() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['XXSSIDXX']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_169() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['ssid']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_170() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(None):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_171() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(None)
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_172() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(None)
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_173() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 1
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def x_do_start__mutmut_174() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(None)
        return 1


def x_do_start__mutmut_175() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 2

mutants_x_do_start__mutmut['_mutmut_orig'] = x_do_start__mutmut_orig # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_1'] = x_do_start__mutmut_1 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_2'] = x_do_start__mutmut_2 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_3'] = x_do_start__mutmut_3 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_4'] = x_do_start__mutmut_4 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_5'] = x_do_start__mutmut_5 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_6'] = x_do_start__mutmut_6 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_7'] = x_do_start__mutmut_7 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_8'] = x_do_start__mutmut_8 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_9'] = x_do_start__mutmut_9 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_10'] = x_do_start__mutmut_10 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_11'] = x_do_start__mutmut_11 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_12'] = x_do_start__mutmut_12 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_13'] = x_do_start__mutmut_13 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_14'] = x_do_start__mutmut_14 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_15'] = x_do_start__mutmut_15 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_16'] = x_do_start__mutmut_16 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_17'] = x_do_start__mutmut_17 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_18'] = x_do_start__mutmut_18 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_19'] = x_do_start__mutmut_19 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_20'] = x_do_start__mutmut_20 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_21'] = x_do_start__mutmut_21 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_22'] = x_do_start__mutmut_22 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_23'] = x_do_start__mutmut_23 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_24'] = x_do_start__mutmut_24 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_25'] = x_do_start__mutmut_25 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_26'] = x_do_start__mutmut_26 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_27'] = x_do_start__mutmut_27 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_28'] = x_do_start__mutmut_28 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_29'] = x_do_start__mutmut_29 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_30'] = x_do_start__mutmut_30 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_31'] = x_do_start__mutmut_31 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_32'] = x_do_start__mutmut_32 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_33'] = x_do_start__mutmut_33 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_34'] = x_do_start__mutmut_34 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_35'] = x_do_start__mutmut_35 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_36'] = x_do_start__mutmut_36 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_37'] = x_do_start__mutmut_37 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_38'] = x_do_start__mutmut_38 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_39'] = x_do_start__mutmut_39 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_40'] = x_do_start__mutmut_40 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_41'] = x_do_start__mutmut_41 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_42'] = x_do_start__mutmut_42 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_43'] = x_do_start__mutmut_43 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_44'] = x_do_start__mutmut_44 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_45'] = x_do_start__mutmut_45 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_46'] = x_do_start__mutmut_46 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_47'] = x_do_start__mutmut_47 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_48'] = x_do_start__mutmut_48 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_49'] = x_do_start__mutmut_49 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_50'] = x_do_start__mutmut_50 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_51'] = x_do_start__mutmut_51 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_52'] = x_do_start__mutmut_52 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_53'] = x_do_start__mutmut_53 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_54'] = x_do_start__mutmut_54 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_55'] = x_do_start__mutmut_55 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_56'] = x_do_start__mutmut_56 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_57'] = x_do_start__mutmut_57 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_58'] = x_do_start__mutmut_58 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_59'] = x_do_start__mutmut_59 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_60'] = x_do_start__mutmut_60 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_61'] = x_do_start__mutmut_61 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_62'] = x_do_start__mutmut_62 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_63'] = x_do_start__mutmut_63 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_64'] = x_do_start__mutmut_64 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_65'] = x_do_start__mutmut_65 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_66'] = x_do_start__mutmut_66 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_67'] = x_do_start__mutmut_67 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_68'] = x_do_start__mutmut_68 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_69'] = x_do_start__mutmut_69 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_70'] = x_do_start__mutmut_70 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_71'] = x_do_start__mutmut_71 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_72'] = x_do_start__mutmut_72 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_73'] = x_do_start__mutmut_73 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_74'] = x_do_start__mutmut_74 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_75'] = x_do_start__mutmut_75 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_76'] = x_do_start__mutmut_76 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_77'] = x_do_start__mutmut_77 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_78'] = x_do_start__mutmut_78 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_79'] = x_do_start__mutmut_79 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_80'] = x_do_start__mutmut_80 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_81'] = x_do_start__mutmut_81 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_82'] = x_do_start__mutmut_82 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_83'] = x_do_start__mutmut_83 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_84'] = x_do_start__mutmut_84 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_85'] = x_do_start__mutmut_85 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_86'] = x_do_start__mutmut_86 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_87'] = x_do_start__mutmut_87 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_88'] = x_do_start__mutmut_88 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_89'] = x_do_start__mutmut_89 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_90'] = x_do_start__mutmut_90 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_91'] = x_do_start__mutmut_91 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_92'] = x_do_start__mutmut_92 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_93'] = x_do_start__mutmut_93 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_94'] = x_do_start__mutmut_94 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_95'] = x_do_start__mutmut_95 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_96'] = x_do_start__mutmut_96 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_97'] = x_do_start__mutmut_97 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_98'] = x_do_start__mutmut_98 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_99'] = x_do_start__mutmut_99 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_100'] = x_do_start__mutmut_100 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_101'] = x_do_start__mutmut_101 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_102'] = x_do_start__mutmut_102 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_103'] = x_do_start__mutmut_103 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_104'] = x_do_start__mutmut_104 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_105'] = x_do_start__mutmut_105 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_106'] = x_do_start__mutmut_106 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_107'] = x_do_start__mutmut_107 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_108'] = x_do_start__mutmut_108 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_109'] = x_do_start__mutmut_109 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_110'] = x_do_start__mutmut_110 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_111'] = x_do_start__mutmut_111 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_112'] = x_do_start__mutmut_112 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_113'] = x_do_start__mutmut_113 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_114'] = x_do_start__mutmut_114 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_115'] = x_do_start__mutmut_115 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_116'] = x_do_start__mutmut_116 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_117'] = x_do_start__mutmut_117 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_118'] = x_do_start__mutmut_118 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_119'] = x_do_start__mutmut_119 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_120'] = x_do_start__mutmut_120 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_121'] = x_do_start__mutmut_121 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_122'] = x_do_start__mutmut_122 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_123'] = x_do_start__mutmut_123 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_124'] = x_do_start__mutmut_124 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_125'] = x_do_start__mutmut_125 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_126'] = x_do_start__mutmut_126 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_127'] = x_do_start__mutmut_127 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_128'] = x_do_start__mutmut_128 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_129'] = x_do_start__mutmut_129 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_130'] = x_do_start__mutmut_130 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_131'] = x_do_start__mutmut_131 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_132'] = x_do_start__mutmut_132 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_133'] = x_do_start__mutmut_133 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_134'] = x_do_start__mutmut_134 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_135'] = x_do_start__mutmut_135 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_136'] = x_do_start__mutmut_136 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_137'] = x_do_start__mutmut_137 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_138'] = x_do_start__mutmut_138 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_139'] = x_do_start__mutmut_139 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_140'] = x_do_start__mutmut_140 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_141'] = x_do_start__mutmut_141 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_142'] = x_do_start__mutmut_142 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_143'] = x_do_start__mutmut_143 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_144'] = x_do_start__mutmut_144 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_145'] = x_do_start__mutmut_145 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_146'] = x_do_start__mutmut_146 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_147'] = x_do_start__mutmut_147 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_148'] = x_do_start__mutmut_148 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_149'] = x_do_start__mutmut_149 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_150'] = x_do_start__mutmut_150 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_151'] = x_do_start__mutmut_151 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_152'] = x_do_start__mutmut_152 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_153'] = x_do_start__mutmut_153 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_154'] = x_do_start__mutmut_154 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_155'] = x_do_start__mutmut_155 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_156'] = x_do_start__mutmut_156 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_157'] = x_do_start__mutmut_157 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_158'] = x_do_start__mutmut_158 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_159'] = x_do_start__mutmut_159 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_160'] = x_do_start__mutmut_160 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_161'] = x_do_start__mutmut_161 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_162'] = x_do_start__mutmut_162 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_163'] = x_do_start__mutmut_163 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_164'] = x_do_start__mutmut_164 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_165'] = x_do_start__mutmut_165 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_166'] = x_do_start__mutmut_166 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_167'] = x_do_start__mutmut_167 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_168'] = x_do_start__mutmut_168 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_169'] = x_do_start__mutmut_169 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_170'] = x_do_start__mutmut_170 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_171'] = x_do_start__mutmut_171 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_172'] = x_do_start__mutmut_172 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_173'] = x_do_start__mutmut_173 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_174'] = x_do_start__mutmut_174 # type: ignore # mutmut generated
mutants_x_do_start__mutmut['x_do_start__mutmut_175'] = x_do_start__mutmut_175 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_do_stop__mutmut)
def do_stop() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_orig() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_1() -> int:
    cfg = None
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_2() -> int:
    cfg = load_env()
    ap = None
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_3() -> int:
    cfg = load_env()
    ap = cfg["XXAP_IFACEXX"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_4() -> int:
    cfg = load_env()
    ap = cfg["ap_iface"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_5() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = None
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_6() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["XXWAN_IFACEXX"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_7() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["wan_iface"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_8() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log(None)
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_9() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("XXDeteniendo AP...XX")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_10() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("deteniendo ap...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_11() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("DETENIENDO AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_12() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(None,
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_13() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=None)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_14() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_15() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        )
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_16() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["XXipXX", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_17() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["IP", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_18() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "XXaddrXX", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_19() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "ADDR", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_20() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "XXdelXX", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_21() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "DEL", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_22() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['XXAP_IPXX']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_23() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['ap_ip']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_24() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['XXAP_CIDRXX']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_25() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['ap_cidr']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_26() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "XXdevXX", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_27() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "DEV", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_28() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=True)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_29() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(None, check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_30() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=None)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_31() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_32() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], )
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_33() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["XXnmcliXX", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_34() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["NMCLI", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_35() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "XXdeviceXX", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_36() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "DEVICE", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_37() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "XXsetXX", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_38() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "SET", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_39() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "XXmanagedXX", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_40() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "MANAGED", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_41() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "XXyesXX"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_42() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "YES"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_43() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=True)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_44() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(None, check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_45() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=None)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_46() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_47() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], )
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_48() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["XXiptablesXX", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_49() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["IPTABLES", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_50() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "XX-tXX", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_51() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-T", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_52() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "XXnatXX", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_53() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "NAT", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_54() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "XX-DXX", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_55() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-d", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_56() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "XXPOSTROUTINGXX", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_57() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "postrouting", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_58() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "XX-oXX", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_59() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-O", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_60() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "XX-sXX", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_61() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-S", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_62() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["XXAP_SUBNETXX"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_63() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["ap_subnet"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_64() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "XX-jXX", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_65() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-J", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_66() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "XXMASQUERADEXX"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_67() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "masquerade"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_68() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=True)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_69() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(None, check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_70() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=None)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_71() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_72() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], )
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_73() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["XXsysctlXX", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_74() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["SYSCTL", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_75() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "XX-wXX", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_76() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-W", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_77() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "XXnet.ipv4.ip_forward=0XX"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_78() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "NET.IPV4.IP_FORWARD=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_79() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=True)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_80() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(None, check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_81() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=None)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_82() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_83() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], )
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_84() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["XXipXX", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_85() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["IP", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_86() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "XXlinkXX", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_87() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "LINK", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_88() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "XXsetXX", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_89() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "SET", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_90() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "XXdownXX"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_91() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "DOWN"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_92() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=True)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_93() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(None)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_94() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(2)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_95() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(None, check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_96() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=None)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_97() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_98() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], )
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_99() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["XXipXX", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_100() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["IP", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_101() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "XXlinkXX", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_102() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "LINK", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_103() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "XXsetXX", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_104() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "SET", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_105() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "XXupXX"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_106() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "UP"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_107() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=True)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def x_do_stop__mutmut_108() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log(None)
    return 0


def x_do_stop__mutmut_109() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("XXAP detenido. iface restaurada a cliente (NM gestionado).XX")
    return 0


def x_do_stop__mutmut_110() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("ap detenido. iface restaurada a cliente (nm gestionado).")
    return 0


def x_do_stop__mutmut_111() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP DETENIDO. IFACE RESTAURADA A CLIENTE (NM GESTIONADO).")
    return 0


def x_do_stop__mutmut_112() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 1

mutants_x_do_stop__mutmut['_mutmut_orig'] = x_do_stop__mutmut_orig # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_1'] = x_do_stop__mutmut_1 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_2'] = x_do_stop__mutmut_2 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_3'] = x_do_stop__mutmut_3 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_4'] = x_do_stop__mutmut_4 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_5'] = x_do_stop__mutmut_5 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_6'] = x_do_stop__mutmut_6 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_7'] = x_do_stop__mutmut_7 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_8'] = x_do_stop__mutmut_8 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_9'] = x_do_stop__mutmut_9 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_10'] = x_do_stop__mutmut_10 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_11'] = x_do_stop__mutmut_11 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_12'] = x_do_stop__mutmut_12 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_13'] = x_do_stop__mutmut_13 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_14'] = x_do_stop__mutmut_14 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_15'] = x_do_stop__mutmut_15 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_16'] = x_do_stop__mutmut_16 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_17'] = x_do_stop__mutmut_17 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_18'] = x_do_stop__mutmut_18 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_19'] = x_do_stop__mutmut_19 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_20'] = x_do_stop__mutmut_20 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_21'] = x_do_stop__mutmut_21 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_22'] = x_do_stop__mutmut_22 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_23'] = x_do_stop__mutmut_23 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_24'] = x_do_stop__mutmut_24 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_25'] = x_do_stop__mutmut_25 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_26'] = x_do_stop__mutmut_26 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_27'] = x_do_stop__mutmut_27 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_28'] = x_do_stop__mutmut_28 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_29'] = x_do_stop__mutmut_29 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_30'] = x_do_stop__mutmut_30 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_31'] = x_do_stop__mutmut_31 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_32'] = x_do_stop__mutmut_32 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_33'] = x_do_stop__mutmut_33 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_34'] = x_do_stop__mutmut_34 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_35'] = x_do_stop__mutmut_35 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_36'] = x_do_stop__mutmut_36 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_37'] = x_do_stop__mutmut_37 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_38'] = x_do_stop__mutmut_38 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_39'] = x_do_stop__mutmut_39 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_40'] = x_do_stop__mutmut_40 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_41'] = x_do_stop__mutmut_41 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_42'] = x_do_stop__mutmut_42 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_43'] = x_do_stop__mutmut_43 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_44'] = x_do_stop__mutmut_44 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_45'] = x_do_stop__mutmut_45 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_46'] = x_do_stop__mutmut_46 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_47'] = x_do_stop__mutmut_47 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_48'] = x_do_stop__mutmut_48 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_49'] = x_do_stop__mutmut_49 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_50'] = x_do_stop__mutmut_50 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_51'] = x_do_stop__mutmut_51 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_52'] = x_do_stop__mutmut_52 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_53'] = x_do_stop__mutmut_53 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_54'] = x_do_stop__mutmut_54 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_55'] = x_do_stop__mutmut_55 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_56'] = x_do_stop__mutmut_56 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_57'] = x_do_stop__mutmut_57 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_58'] = x_do_stop__mutmut_58 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_59'] = x_do_stop__mutmut_59 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_60'] = x_do_stop__mutmut_60 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_61'] = x_do_stop__mutmut_61 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_62'] = x_do_stop__mutmut_62 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_63'] = x_do_stop__mutmut_63 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_64'] = x_do_stop__mutmut_64 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_65'] = x_do_stop__mutmut_65 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_66'] = x_do_stop__mutmut_66 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_67'] = x_do_stop__mutmut_67 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_68'] = x_do_stop__mutmut_68 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_69'] = x_do_stop__mutmut_69 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_70'] = x_do_stop__mutmut_70 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_71'] = x_do_stop__mutmut_71 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_72'] = x_do_stop__mutmut_72 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_73'] = x_do_stop__mutmut_73 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_74'] = x_do_stop__mutmut_74 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_75'] = x_do_stop__mutmut_75 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_76'] = x_do_stop__mutmut_76 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_77'] = x_do_stop__mutmut_77 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_78'] = x_do_stop__mutmut_78 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_79'] = x_do_stop__mutmut_79 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_80'] = x_do_stop__mutmut_80 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_81'] = x_do_stop__mutmut_81 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_82'] = x_do_stop__mutmut_82 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_83'] = x_do_stop__mutmut_83 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_84'] = x_do_stop__mutmut_84 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_85'] = x_do_stop__mutmut_85 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_86'] = x_do_stop__mutmut_86 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_87'] = x_do_stop__mutmut_87 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_88'] = x_do_stop__mutmut_88 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_89'] = x_do_stop__mutmut_89 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_90'] = x_do_stop__mutmut_90 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_91'] = x_do_stop__mutmut_91 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_92'] = x_do_stop__mutmut_92 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_93'] = x_do_stop__mutmut_93 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_94'] = x_do_stop__mutmut_94 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_95'] = x_do_stop__mutmut_95 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_96'] = x_do_stop__mutmut_96 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_97'] = x_do_stop__mutmut_97 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_98'] = x_do_stop__mutmut_98 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_99'] = x_do_stop__mutmut_99 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_100'] = x_do_stop__mutmut_100 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_101'] = x_do_stop__mutmut_101 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_102'] = x_do_stop__mutmut_102 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_103'] = x_do_stop__mutmut_103 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_104'] = x_do_stop__mutmut_104 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_105'] = x_do_stop__mutmut_105 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_106'] = x_do_stop__mutmut_106 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_107'] = x_do_stop__mutmut_107 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_108'] = x_do_stop__mutmut_108 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_109'] = x_do_stop__mutmut_109 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_110'] = x_do_stop__mutmut_110 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_111'] = x_do_stop__mutmut_111 # type: ignore # mutmut generated
mutants_x_do_stop__mutmut['x_do_stop__mutmut_112'] = x_do_stop__mutmut_112 # type: ignore # mutmut generated
mutants_x_do_status__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_do_status__mutmut)
def do_status() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_orig() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_1() -> int:
    cfg = None
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_2() -> int:
    cfg = load_env()
    ap = None
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_3() -> int:
    cfg = load_env()
    ap = cfg["XXAP_IFACEXX"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_4() -> int:
    cfg = load_env()
    ap = cfg["ap_iface"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_5() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = None
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_6() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["XXWAN_IFACEXX"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_7() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["wan_iface"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_8() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(None)
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_9() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(None)
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_10() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(None)
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_11() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = None
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_12() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(None, capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_13() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=None)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_14() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_15() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], )
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_16() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["XXiwXX", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_17() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["IW", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_18() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "XXdevXX", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_19() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "DEV", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_20() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "XXinfoXX"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_21() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "INFO"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_22() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=False)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_23() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 or "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_24() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode != 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_25() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 1 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_26() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "XXtype APXX" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_27() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type ap" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_28() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "TYPE AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_29() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" not in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_30() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout and ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_31() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or "XXXX"):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_32() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print(None)
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_33() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("XXModo:        AP (activo)XX")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_34() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("modo:        ap (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_35() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("MODO:        AP (ACTIVO)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_36() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(None)
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_37() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['XXAP_IPXX']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_38() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['ap_ip']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_39() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['XXAP_CIDRXX']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_40() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['ap_cidr']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_41() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(None)
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_42() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['XXSSIDXX']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_43() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['ssid']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_44() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print(None)
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_45() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("XXModo:        CLIENTE (AP inactivo)XX")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_46() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("modo:        cliente (ap inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_47() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("MODO:        CLIENTE (AP INACTIVO)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_48() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = None
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_49() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(None, capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_50() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=None)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_51() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_52() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], )
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_53() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["XXsystemctlXX", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_54() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["SYSTEMCTL", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_55() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "XXis-activeXX", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_56() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "IS-ACTIVE", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_57() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "XXescama-ap.serviceXX"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_58() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "ESCAMA-AP.SERVICE"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_59() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=False)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def x_do_status__mutmut_60() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(None)
    return 0


def x_do_status__mutmut_61() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout and '').strip()}")
    return 0


def x_do_status__mutmut_62() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or 'XXXX').strip()}")
    return 0


def x_do_status__mutmut_63() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 1

mutants_x_do_status__mutmut['_mutmut_orig'] = x_do_status__mutmut_orig # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_1'] = x_do_status__mutmut_1 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_2'] = x_do_status__mutmut_2 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_3'] = x_do_status__mutmut_3 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_4'] = x_do_status__mutmut_4 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_5'] = x_do_status__mutmut_5 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_6'] = x_do_status__mutmut_6 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_7'] = x_do_status__mutmut_7 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_8'] = x_do_status__mutmut_8 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_9'] = x_do_status__mutmut_9 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_10'] = x_do_status__mutmut_10 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_11'] = x_do_status__mutmut_11 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_12'] = x_do_status__mutmut_12 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_13'] = x_do_status__mutmut_13 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_14'] = x_do_status__mutmut_14 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_15'] = x_do_status__mutmut_15 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_16'] = x_do_status__mutmut_16 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_17'] = x_do_status__mutmut_17 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_18'] = x_do_status__mutmut_18 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_19'] = x_do_status__mutmut_19 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_20'] = x_do_status__mutmut_20 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_21'] = x_do_status__mutmut_21 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_22'] = x_do_status__mutmut_22 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_23'] = x_do_status__mutmut_23 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_24'] = x_do_status__mutmut_24 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_25'] = x_do_status__mutmut_25 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_26'] = x_do_status__mutmut_26 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_27'] = x_do_status__mutmut_27 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_28'] = x_do_status__mutmut_28 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_29'] = x_do_status__mutmut_29 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_30'] = x_do_status__mutmut_30 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_31'] = x_do_status__mutmut_31 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_32'] = x_do_status__mutmut_32 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_33'] = x_do_status__mutmut_33 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_34'] = x_do_status__mutmut_34 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_35'] = x_do_status__mutmut_35 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_36'] = x_do_status__mutmut_36 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_37'] = x_do_status__mutmut_37 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_38'] = x_do_status__mutmut_38 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_39'] = x_do_status__mutmut_39 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_40'] = x_do_status__mutmut_40 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_41'] = x_do_status__mutmut_41 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_42'] = x_do_status__mutmut_42 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_43'] = x_do_status__mutmut_43 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_44'] = x_do_status__mutmut_44 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_45'] = x_do_status__mutmut_45 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_46'] = x_do_status__mutmut_46 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_47'] = x_do_status__mutmut_47 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_48'] = x_do_status__mutmut_48 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_49'] = x_do_status__mutmut_49 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_50'] = x_do_status__mutmut_50 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_51'] = x_do_status__mutmut_51 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_52'] = x_do_status__mutmut_52 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_53'] = x_do_status__mutmut_53 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_54'] = x_do_status__mutmut_54 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_55'] = x_do_status__mutmut_55 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_56'] = x_do_status__mutmut_56 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_57'] = x_do_status__mutmut_57 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_58'] = x_do_status__mutmut_58 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_59'] = x_do_status__mutmut_59 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_60'] = x_do_status__mutmut_60 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_61'] = x_do_status__mutmut_61 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_62'] = x_do_status__mutmut_62 # type: ignore # mutmut generated
mutants_x_do_status__mutmut['x_do_status__mutmut_63'] = x_do_status__mutmut_63 # type: ignore # mutmut generated
mutants_x_main__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_main__mutmut)
def main() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_orig() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_1() -> int:
    if os.geteuid() == 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_2() -> int:
    if os.geteuid() != 1:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_3() -> int:
    if os.geteuid() != 0:
        print(None, file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_4() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=None)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_5() -> int:
    if os.geteuid() != 0:
        print(file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_6() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", )
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_7() -> int:
    if os.geteuid() != 0:
        print("XXEste script necesita sudo. Ejecutalo con: sudo escama.py ...XX", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_8() -> int:
    if os.geteuid() != 0:
        print("este script necesita sudo. ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_9() -> int:
    if os.geteuid() != 0:
        print("ESTE SCRIPT NECESITA SUDO. EJECUTALO CON: SUDO ESCAMA.PY ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_10() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 2
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_11() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = None
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_12() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[2] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_13() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) >= 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_14() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 2 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_15() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "XXstatusXX"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_16() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "STATUS"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_17() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action != "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_18() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "XXstartXX":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_19() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "START":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_20() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action != "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_21() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "XXstopXX":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_22() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "STOP":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_23() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action != "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_24() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "XXrestartXX":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_25() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "RESTART":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_26() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(None)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_27() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(2)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_28() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action != "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_29() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "XXstatusXX":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_30() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "STATUS":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_31() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action != "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_32() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "XXreconnectXX":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_33() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "RECONNECT":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_34() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = None
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_35() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_36() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(None):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_37() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["XXAP_IFACEXX"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_38() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["ap_iface"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_39() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(None)
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_40() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['XXAP_IFACEXX']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_41() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['ap_iface']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_42() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 2
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_43() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(None)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_44() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(2)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_45() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action != "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_46() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "XXgenconfigXX":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_47() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "GENCONFIG":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_48() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(None)
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_49() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log(None)
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_50() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("XXConfigs generados.XX")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_51() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_52() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("CONFIGS GENERADOS.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_53() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 1
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_54() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(None, file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_55() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=None)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_56() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_57() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", )
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_58() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print(None, file=sys.stderr)
        return 2


def x_main__mutmut_59() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=None)
        return 2


def x_main__mutmut_60() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print(file=sys.stderr)
        return 2


def x_main__mutmut_61() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", )
        return 2


def x_main__mutmut_62() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("XXUso: escama.py {start|stop|restart|status|reconnect|genconfig}XX", file=sys.stderr)
        return 2


def x_main__mutmut_63() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 2


def x_main__mutmut_64() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("USO: ESCAMA.PY {START|STOP|RESTART|STATUS|RECONNECT|GENCONFIG}", file=sys.stderr)
        return 2


def x_main__mutmut_65() -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama.py ...", file=sys.stderr)
        return 1
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: escama.py {start|stop|restart|status|reconnect|genconfig}", file=sys.stderr)
        return 3

mutants_x_main__mutmut['_mutmut_orig'] = x_main__mutmut_orig # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_1'] = x_main__mutmut_1 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_2'] = x_main__mutmut_2 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_3'] = x_main__mutmut_3 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_4'] = x_main__mutmut_4 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_5'] = x_main__mutmut_5 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_6'] = x_main__mutmut_6 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_7'] = x_main__mutmut_7 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_8'] = x_main__mutmut_8 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_9'] = x_main__mutmut_9 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_10'] = x_main__mutmut_10 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_11'] = x_main__mutmut_11 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_12'] = x_main__mutmut_12 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_13'] = x_main__mutmut_13 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_14'] = x_main__mutmut_14 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_15'] = x_main__mutmut_15 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_16'] = x_main__mutmut_16 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_17'] = x_main__mutmut_17 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_18'] = x_main__mutmut_18 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_19'] = x_main__mutmut_19 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_20'] = x_main__mutmut_20 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_21'] = x_main__mutmut_21 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_22'] = x_main__mutmut_22 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_23'] = x_main__mutmut_23 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_24'] = x_main__mutmut_24 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_25'] = x_main__mutmut_25 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_26'] = x_main__mutmut_26 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_27'] = x_main__mutmut_27 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_28'] = x_main__mutmut_28 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_29'] = x_main__mutmut_29 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_30'] = x_main__mutmut_30 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_31'] = x_main__mutmut_31 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_32'] = x_main__mutmut_32 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_33'] = x_main__mutmut_33 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_34'] = x_main__mutmut_34 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_35'] = x_main__mutmut_35 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_36'] = x_main__mutmut_36 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_37'] = x_main__mutmut_37 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_38'] = x_main__mutmut_38 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_39'] = x_main__mutmut_39 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_40'] = x_main__mutmut_40 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_41'] = x_main__mutmut_41 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_42'] = x_main__mutmut_42 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_43'] = x_main__mutmut_43 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_44'] = x_main__mutmut_44 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_45'] = x_main__mutmut_45 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_46'] = x_main__mutmut_46 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_47'] = x_main__mutmut_47 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_48'] = x_main__mutmut_48 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_49'] = x_main__mutmut_49 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_50'] = x_main__mutmut_50 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_51'] = x_main__mutmut_51 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_52'] = x_main__mutmut_52 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_53'] = x_main__mutmut_53 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_54'] = x_main__mutmut_54 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_55'] = x_main__mutmut_55 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_56'] = x_main__mutmut_56 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_57'] = x_main__mutmut_57 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_58'] = x_main__mutmut_58 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_59'] = x_main__mutmut_59 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_60'] = x_main__mutmut_60 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_61'] = x_main__mutmut_61 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_62'] = x_main__mutmut_62 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_63'] = x_main__mutmut_63 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_64'] = x_main__mutmut_64 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_65'] = x_main__mutmut_65 # type: ignore # mutmut generated


if __name__ == "__main__":
    sys.exit(main())
