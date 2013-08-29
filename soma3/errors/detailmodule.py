
from urqa.models import Errors

def manual_auto_determine(errorelement):
    boldstr = '<span class="bold">'
    manualstr = 'Manual</span>&nbsp;'
    autostr = 'Auto'

    manual_autostr = ""
    if errorelement.autodetermine == 1:
        manual_autostr = manualstr + boldstr + autostr
    else:
        manual_autostr = boldstr + manualstr + autostr

    return manual_autostr

