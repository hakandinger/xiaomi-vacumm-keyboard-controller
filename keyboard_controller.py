import os
import sys
import time
import threading

import pygame
from miio import ViomiVacuum

IP = os.environ.get("MIIO_IP")
TOKEN = os.environ.get("MIIO_TOKEN")

if not IP or not TOKEN:
    sys.exit("MIIO_IP veya MIIO_TOKEN tanımlı değil.")

STOP = 5
DIRECTIONS = {
    pygame.K_UP:    ("İleri", 1),
    pygame.K_DOWN:  ("Geri", 4),
    pygame.K_LEFT:  ("Sol", 2),
    pygame.K_RIGHT: ("Sağ", 3),
}


REFRESH_MOVE = 0.5      # tuş basılıyken komut yenileme (sn), 0 = kapalı
WARMUP_MAX = 30         # ısınma için en fazla bekleme (sn)

robot = ViomiVacuum(IP, TOKEN)
import pathlib

TIMEOUT = 3.0
ID_FILE = pathlib.Path(__file__).with_name(".miio_id")
sent = 0          # gönderilen komut sayısı (id'nin yaklaşık takibi)
start_id_used = 0


def load_start_id():
    try:
        return int(ID_FILE.read_text())
    except Exception:
        return 0


def save_start_id():
    try:
        ID_FILE.write_text(str((start_id_used + sent + 200) % 9000))
    except OSError:
        pass


def make_robot(start_id):
    r = ViomiVacuum(IP, TOKEN, start_id=start_id)
    try:
        r._protocol._timeout = TIMEOUT
    except AttributeError:
        pass
    return r


def send(method, params):
    global sent
    sent += 1
    return robot.send(method, params, retry_count=0)


def warm_up():
    global robot, start_id_used, sent
    base = load_start_id()
    for k in range(8):
        sid = (base + k * 300) % 9000
        robot = make_robot(sid)
        start_id_used, sent = sid, 0
        for i in range(2):
            t = time.monotonic()
            try:
                send("set_direction", [STOP])
                print(f"Bağlantı hazır (start_id={sid}, "
                      f"{(time.monotonic() - t) * 1000:.0f} ms)", flush=True)
                return True
            except Exception as exc:
                print(f"Isınma start_id={sid}: yanıt yok ({type(exc).__name__})",
                      flush=True)
    return False


robot = None
print("Süpürgeyle bağlantı kuruluyor...", flush=True)
if not warm_up():
    sys.exit("Süpürge yön komutuna yanıt vermedi.")
def warm_up():
    """Zararsız 'Dur' komutuyla yön komutu yolunu açar."""
    end = time.monotonic() + WARMUP_MAX
    n = 0
    while time.monotonic() < end:
        n += 1
        t = time.monotonic()
        try:
            robot.send("set_direction", [STOP], retry_count=0)
            print(f"Bağlantı hazır ({n}. deneme, "
                  f"{(time.monotonic() - t) * 1000:.0f} ms)", flush=True)
            return True
        except Exception as exc:
            print(f"Isınma {n}: yanıt yok ({type(exc).__name__})", flush=True)
            time.sleep(0.5)
    return False


print("Süpürgeyle bağlantı kuruluyor...", flush=True)
if not warm_up():
    sys.exit("Süpürge yön komutuna yanıt vermedi. Biraz bekleyip tekrar dene.")

condition = threading.Condition()
desired_name = "Dur"
desired_value = STOP
revision = 0
closing = False

robot_lock = threading.Lock()
horn_cooldown = 1.5
last_horn_time = 0.0


def play_horn():
    global last_horn_time
    now = time.monotonic()
    if now - last_horn_time < horn_cooldown:
        return
    last_horn_time = now
    try:
        horn_sounds[horn_index].play()
        print("Korna çalındı.", flush=True)
    except Exception as exc:
        print(f"Korna başarısız: {type(exc).__name__}: {exc}", flush=True)

ACTIONS = {
    pygame.K_h:      ("Şarja dön",         "set_charge",        [1]),
    pygame.K_RETURN: ("Temizliği başlat",  "set_mode_withroom", [0, 1, 0]),
    pygame.K_p:      ("Duraklat",          "set_mode_withroom", [0, 2, 0]),
    pygame.K_x:      ("Temizliği bitir",   "set_mode",          [0]),
}
ACTION_COOLDOWN = 1.0
last_action_time = 0.0
led_on = True   # başlangıç durumu bilinmiyor, açık varsayıldı


def run_action(label, method, params):
    global last_action_time
    now = time.monotonic()
    if now - last_action_time < ACTION_COOLDOWN:
        return
    last_action_time = now
    try:
        with robot_lock:
            result = send(method, params)
        print(f"{label}: {result}", flush=True)
    except Exception as exc:
        print(f"{label} başarısız: {type(exc).__name__}", flush=True)


def toggle_led():
    global led_on
    led_on = not led_on
    run_action(f"LED {'açık' if led_on else 'kapalı'}", "set_light", [1 if led_on else 0])


def set_desired(name, value):
    global desired_name, desired_value, revision
    with condition:
        desired_name = name
        desired_value = value
        revision += 1
        condition.notify_all()


def network_worker():
    last_revision = 0
    last_ok = 0.0
    last_try = 0.0
    stop_confirmed = True
    stop_fail = 0

    while True:
        with condition:
            condition.wait_for(
                lambda: revision != last_revision or closing,
                timeout=0.2,
            )
            name = desired_name
            value = desired_value
            cur_rev = revision
            is_closing = closing

        now = time.monotonic()
        changed = cur_rev != last_revision

        if value == STOP:
            need = changed or not stop_confirmed
            retry_delay = 0.3 if stop_fail < 5 else 1.0
        else:
            need = changed or (REFRESH_MOVE > 0 and now - last_ok >= REFRESH_MOVE)
            retry_delay = 0.5

        # Yeni bir tuş olayı yoksa, başarısız denemeler arasında bekle.
        if need and not changed and now - last_try < retry_delay:
            need = False

        if need:
            last_try = time.monotonic()
            try:
                with robot_lock:
                    result = robot.send("set_direction", [value])
                ms = (time.monotonic() - last_try) * 1000
                print(f"{name}: {result} | {ms:.0f} ms", flush=True)
                last_ok = time.monotonic()
                stop_confirmed = (value == STOP)
                stop_fail = 0
            except Exception as exc:
                print(f"{name} başarısız: {type(exc).__name__}", flush=True)
                if value == STOP:
                    stop_confirmed = False
                    stop_fail += 1
                    if stop_fail == 5:
                        print("Cihaz Dur komutuna yanıt vermiyor, "
                              "robotu elle durdur!", flush=True)
            last_revision = cur_rev
        elif changed:
            last_revision = cur_rev

        if is_closing and value == STOP and stop_confirmed:
            return


worker = threading.Thread(target=network_worker, daemon=True)
worker.start()

pygame.init()
screen = pygame.display.set_mode((460, 300))
pygame.display.set_caption("Viomi Robot - Klavye Kontrolü")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 22)

pygame.mixer.init()
SOUND_FILES = ["horn.wav"]   # birden fazla ses için: ["horn.wav", "horn2.wav"]
horn_sounds = []
for f in SOUND_FILES:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f)
    try:
        horn_sounds.append(pygame.mixer.Sound(path))
    except Exception as exc:
        print(f"{f} yüklenemedi: {exc}", flush=True)
if not horn_sounds:
    print("Hiç korna sesi yüklenemedi, boşluk tuşu çalışmayacak.", flush=True)
horn_index = 0

pressed_keys = []
running = True
last_name = "Dur"

print("Klavye kontrolü hazır.", flush=True)
print("Yön tuşları: hareket | Boşluk: korna | Tuşu bırak: dur | ESC: çıkış",
      flush=True)

try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    threading.Thread(target=play_horn, daemon=True).start()
                
                elif event.key in ACTIONS:
                    label, method, params = ACTIONS[event.key]
                    threading.Thread(target=run_action, args=(label, method, params), daemon=True).start()
                elif event.key == pygame.K_l:
                    threading.Thread(target=toggle_led, daemon=True).start()

                elif event.key in DIRECTIONS:
                    if event.key in pressed_keys:
                        pressed_keys.remove(event.key)
                    pressed_keys.append(event.key)
                    name, value = DIRECTIONS[event.key]
                    last_name = name
                    set_desired(name, value)

            elif event.type == pygame.KEYUP:
                if event.key in DIRECTIONS and event.key in pressed_keys:
                    pressed_keys.remove(event.key)
                    if not pressed_keys:
                        last_name = "Dur"
                        set_desired("Dur", STOP)
                    else:
                        name, value = DIRECTIONS[pressed_keys[-1]]
                        last_name = name
                        set_desired(name, value)

        screen.fill((28, 32, 40))
        screen.blit(font.render("Viomi Robot Kontrolü", True, (255, 255, 255)), (35, 40))
        screen.blit(font.render(f"Durum: {last_name}", True, (100, 220, 150)), (35, 105))
        screen.blit(small_font.render("Ok tuslari: hareket | Bosluk: korna | ESC: cikis",
                                      True, (220, 220, 220)), (35, 190))
        screen.blit(small_font.render("Tusu birakinca robot durur.",
                                      True, (220, 220, 220)), (35, 225))
        pygame.display.flip()
        clock.tick(60)

finally:
    pressed_keys.clear()
    set_desired("Dur", STOP)
    with condition:
        closing = True
        condition.notify_all()
    worker.join(timeout=8)
    save_start_id()
    pygame.quit()
    print("Kontrol penceresi kapatıldı.", flush=True)