
from urqa.models import Errors

def manual_auto_determine(errorelement):
    boldstr = '<span class="bold">'
    boldstrend = '</span>&nbsp;'
    manualstr = 'Manual'
    autostr = 'Auto'

    manual_autostr = ""
    if errorelement.autodetermine == 1:
        manual_autostr = manualstr + boldstr + autostr + boldstrend
    else:
        manual_autostr = boldstr + manualstr + boldstrend +autostr

    print manual_autostr
    return manual_autostr

