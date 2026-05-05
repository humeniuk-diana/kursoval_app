from .constants import PALETTE, FONT
from .utils import get_model_id, get_model_name, get_answer_text
from .widgets import GlassButton, ProgressBar
from .base_page import GradientPage, AuthPage, ChoicePage
from .pages_auth import StartPage, LoginPage, RegisterPage
from .pages_learning import LanguagePage, LevelPage, DashboardPage, AccountPage
from .pages_task import TaskPage
#файл для зручного імпорту, щоб не вказувати повний шлях до файлу

__all__ = [
    "PALETTE", "FONT",
    "get_model_id", "get_model_name", "get_answer_text",
    "GlassButton", "ProgressBar",
    "GradientPage", "AuthPage", "ChoicePage",
    "StartPage", "LoginPage", "RegisterPage",
    "LanguagePage", "LevelPage", "DashboardPage", "AccountPage",
    "TaskPage",
]