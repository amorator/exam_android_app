from typing import Optional, Callable
from kivy.utils import platform as kivy_platform

try:
    from plyer import flashlight as plyer_flashlight  # type: ignore
except Exception:
    plyer_flashlight = None  # type: ignore

try:
    from plyer import brightness as plyer_brightness  # type: ignore
except Exception:
    plyer_brightness = None  # type: ignore


class AndroidUtils:
    """Утилиты Android: фонарик и яркость.

    На десктопе методы безопасно ничего не делают.
    На Android для яркости используем app-level установку через Window.setAttributes.
    При необходимости можем открыть системный экран выдачи спец-разрешения WRITE_SETTINGS.
    Все изменения яркости выполняются на UI-потоке Android для предотвращения crashes.
    """

    def __init__(self) -> None:
        self._flashlight_on: bool = False
        # Сохраняем исходное значение яркости окна: >0.0 явное значение, -1.0 означает "по умолчанию"
        self._original_brightness: Optional[float] = None

    # Flashlight
    def toggle_flashlight(self) -> bool:
        """Переключает фонарик. Сначала пробует Plyer, затем CameraManager."""
        # Try plyer first
        if plyer_flashlight is not None:
            try:
                if self._flashlight_on:
                    plyer_flashlight.off()
                    self._flashlight_on = False
                else:
                    plyer_flashlight.on()
                    self._flashlight_on = True
                return self._flashlight_on
            except Exception as e:
                import traceback
                error_details = f"Plyer flashlight error:\n{type(e).__name__}: {e}\n{traceback.format_exc()}"
                self._show_error(error_details)
        # Fallback to CameraManager on Android
        if kivy_platform == 'android':
            try:
                from jnius import autoclass, cast
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Context = autoclass('android.content.Context')
                CameraManager = autoclass('android.hardware.camera2.CameraManager')
                activity = PythonActivity.mActivity
                cam_service = activity.getSystemService(Context.CAMERA_SERVICE)
                cam_manager = cast('android.hardware.camera2.CameraManager', cam_service)
                ids = cam_manager.getCameraIdList()
                if ids and len(ids) > 0:
                    cam_id = ids[0]
                    self._flashlight_on = not self._flashlight_on
                    cam_manager.setTorchMode(cam_id, bool(self._flashlight_on))
                    return self._flashlight_on
            except Exception as e:
                import traceback
                error_details = f"Android flashlight error:\n{type(e).__name__}: {e}\n{traceback.format_exc()}"
                self._show_error(error_details)
        return self._flashlight_on

    def turn_off_flashlight(self) -> None:
        """Выключает фонарик принудительно."""
        if plyer_flashlight is None:
            return
        try:
            plyer_flashlight.off()
            self._flashlight_on = False
        except Exception:
            pass

    def is_flashlight_on(self) -> bool:
        """Проверяет, включен ли фонарик."""
        return self._flashlight_on

    # Brightness
    def set_brightness(self, value: float) -> None:
        """Устанавливает яркость экрана (app-level на Android)."""
        value = max(0.05, min(1.0, value))
        # Prefer app-level brightness on Android via pyjnius
        if kivy_platform == 'android':
            try:
                from jnius import autoclass, cast
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                WindowManager_LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
                activity = PythonActivity.mActivity
                window = activity.getWindow()
                lp = window.getAttributes()
                lp.screenBrightness = float(value)
                window.setAttributes(lp)
                return
            except Exception:
                pass
        # Fallback to plyer brightness
        if plyer_brightness is not None:
            try:
                plyer_brightness.set_level(value)
            except Exception:
                pass

    def get_brightness(self) -> Optional[float]:
        """Получает текущую яркость экрана."""
        if kivy_platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                window = activity.getWindow()
                lp = window.getAttributes()
                if lp.screenBrightness > 0:
                    return float(lp.screenBrightness)
            except Exception:
                pass
        if plyer_brightness is not None:
            try:
                level = plyer_brightness.get_level()
                if level is None:
                    return None
                return float(level)
            except Exception:
                return None
        return None

    def toggle_brightness_max(self) -> bool:
        """Переключает между максимальной и сохраненной яркостью."""
        try:
            if self._original_brightness is None:
                # Запоминаем текущее состояние окна: если не задано (<=0), помечаем как -1.0 (дефолт)
                self._original_brightness = self._get_current_window_brightness_marker()
                self._set_brightness_android_or_plyer(1.0, allow_default=False)
                # Если не получилось и устройство требует системное разрешение — предложим его выдать
                if kivy_platform == 'android' and not self._is_app_brightness_effective():
                    self._request_write_settings_permission()
                return True
            else:
                # Восстанавливаем: поддерживаем -1.0 как "снять оверрайд"
                self._set_brightness_android_or_plyer(self._original_brightness, allow_default=True)
                self._original_brightness = None
                return False
        except Exception:
            return self._original_brightness is not None

    def toggle_brightness(self) -> bool:
        """Переключает яркость (совместимость с UI). Возвращает True если режим максимальной яркости активен."""
        return self.toggle_brightness_max()

    # Internal
    def _set_brightness_android_or_plyer(self, value: float, allow_default: bool = False) -> None:
        # Если разрешаем default и передано < 0 — снимаем оверрайд (устанавливаем -1)
        if allow_default and value < 0:
            pass  # передадим как -1.0 ниже
        else:
            value = max(0.05, min(1.0, value))
        if kivy_platform == 'android':
            # Используем только app-level яркость (не требует разрешений)
            try:
                from jnius import autoclass, PythonJavaClass, java_method

                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity

                # Выполним изменение яркости на UI-потоке Android
                def _apply():
                    window = activity.getWindow()
                    lp = window.getAttributes()
                    lp.screenBrightness = float(-1.0 if (allow_default and value < 0) else value)
                    window.setAttributes(lp)

                class _Runnable(PythonJavaClass):
                    __javainterfaces__ = ['java/lang/Runnable']
                    def __init__(self, func: Callable[[], None]):
                        super().__init__()
                        self._func = func
                    @java_method('()V')
                    def run(self) -> None:
                        self._func()

                activity.runOnUiThread(_Runnable(_apply))
                return
            except Exception as e:
                import traceback
                error_details = f"Android app-level brightness error:\n{type(e).__name__}: {e}\n{traceback.format_exc()}"
                self._show_error(error_details)

            # На Android не падаем к plyer, чтобы не ловить WRITE_SETTINGS ошибки
            return

        # На не-Android платформах можно попробовать plyer
        if plyer_brightness is not None and kivy_platform != 'android':
            try:
                plyer_brightness.set_level(value)
            except Exception as e:
                import traceback
                error_details = f"Plyer brightness error:\n{type(e).__name__}: {e}\n{traceback.format_exc()}"
                self._show_error(error_details)

    def _get_current_window_brightness_marker(self) -> float:
        """Возвращает текущее значение яркости окна: >0.0 или -1.0 если используется системное по умолчанию."""
        if kivy_platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                window = activity.getWindow()
                lp = window.getAttributes()
                if lp.screenBrightness and lp.screenBrightness > 0:
                    return float(lp.screenBrightness)
                return -1.0
            except Exception:
                return -1.0
        # На других платформах просто вернем -1.0 (нет оверрайда)
        return -1.0

    def restore_brightness_if_needed(self) -> None:
        """Восстанавливает исходную яркость, если до этого было включено максимальное значение."""
        try:
            if self._original_brightness is not None:
                self._set_brightness_android_or_plyer(self._original_brightness, allow_default=True)
                self._original_brightness = None
        except Exception:
            self._original_brightness = None

    def has_brightness(self) -> bool:
        """Проверяет, доступна ли функция яркости."""
        return plyer_brightness is not None

    def has_flashlight(self) -> bool:
        """Проверяет, доступен ли фонарик."""
        return plyer_flashlight is not None

    def _show_error(self, message: str) -> None:
        """Показывает ошибку в GUI вместо print."""
        try:
            from .debug_utils import show_error_popup
            show_error_popup("Ошибка Android", message)
        except Exception:
            # Если не можем показать GUI, хотя бы в лог
            from kivy.logger import Logger
            Logger.error(f"AndroidUtils: {message}")

    # ---- Helpers for WRITE_SETTINGS special permission ----
    def _is_app_brightness_effective(self) -> bool:
        """Проверяет, влияет ли изменение app-level яркости (грубая эвристика)."""
        try:
            if kivy_platform != 'android':
                return True
            before = self.get_brightness() or 0.5
            target = 1.0 if before < 0.9 else 0.2
            self.set_brightness(target)
            after = self.get_brightness() or target
            # Вернем обратно
            self.set_brightness(before)
            return abs(after - target) < 0.05
        except Exception:
            return False

    def _request_write_settings_permission(self) -> None:
        """Открывает системный экран для выдачи WRITE_SETTINGS (если требуется)."""
        try:
            if kivy_platform != 'android':
                return
            from jnius import autoclass, cast
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Settings = autoclass('android.provider.Settings')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            activity = PythonActivity.mActivity
            pkg = activity.getPackageName()
            if not Settings.System.canWrite(activity):
                uri = Uri.parse(f"package:{pkg}")
                intent = Intent(Settings.ACTION_MANAGE_WRITE_SETTINGS, uri)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                activity.startActivity(intent)
                # Покажем подсказку пользователю
                try:
                    from .debug_utils import show_debug_info
                    show_debug_info("Разрешение", "Разрешите изменение системных настроек, затем вернитесь в приложение.")
                except Exception:
                    pass
        except Exception as e:
            import traceback
            error_details = f"WRITE_SETTINGS intent error:\n{type(e).__name__}: {e}\n{traceback.format_exc()}"
            self._show_error(error_details)


