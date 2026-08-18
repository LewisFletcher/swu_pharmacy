from allauth.account.forms import ResetPasswordForm as BaseResetPasswordForm
from allauth.account.forms import SignupForm as BaseSignupForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

# Google's suggested starting threshold; scores range 0.0 (bot) to 1.0 (human).
# Adjust based on the Admin Console's score distribution once there's traffic.
RECAPTCHA_V3_SCORE = 0.5


class SignupForm(BaseSignupForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3(action='signup', required_score=RECAPTCHA_V3_SCORE))


class ResetPasswordForm(BaseResetPasswordForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3(action='reset_password', required_score=RECAPTCHA_V3_SCORE))
