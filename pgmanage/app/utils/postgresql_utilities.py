import os
import shutil

from app.models.main import UserDetails


def get_utility_path(utility, current_user):
    user_d = UserDetails.objects.get(user=current_user)

    if not user_d.binary_path:
        utility_path = shutil.which(utility)
    else:
        utility_path = os.path.join(
            user_d.binary_path, utility if os.name != "nt" else (utility + ".exe")
        )

    if utility_path is None or not os.path.exists(utility_path):
        msg = f"<b>{utility_path if utility_path else utility}</b> not found.<br>\
              Please make sure that you have Postgresql Client installed.<br><b>More information</b>\
              <a href='https://pgmanage.readthedocs.io/en/latest/en/02_quick_start.html#install-guide'>Postgresql Client Installation</a>"
        raise FileNotFoundError(msg)
    return utility_path
