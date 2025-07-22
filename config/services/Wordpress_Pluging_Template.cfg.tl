[Service]

# To adapt this template to any Wordpress Plugin replace EXACT_PLUGING_NAME
#     with the name that it has in the update mails (without spaces at the beginning or end)

# Any Regex is defined without "" even if syntax highlighting looks weird

# Match to this service config file if this RegEx return anything but nothing
email_subject_regex = (\[.+\]) Einige Plugins

# This defines the service name that will appear in CheckMk
# EMAIL_SUBJECT_REGEX will be replaced by the match group from email_subject_regex
name = EMAIL_SUBJECT_REGEX Wordpress Plugin EXACT_PLUGING_NAME

# These define the RegEx that will check the email body for their respective statuses
ok_regex = neuesten Stand:\n- (?:.*\n- )*EXACT_PLUGING_NAME \((.+)\)
warn_regex = nicht aktualisiert werden:\n- (?:.*\n- )*EXACT_PLUGING_NAME \((.+)\)

# Either crit_regex or crit_cycle is required
# This defines how many hours must pass before a WARN is upgraded to a CRIT
crit_cycle = 48

# These define what should be in the service details that are sent to CheckMk
# REGEX_GROUP will be replaced with the capture group from the respective RegEx
#     if you want to provide more deatils like the version number in this case
ok_details = EMAIL_SUBJECT_REGEX Das Wordpress Plugin EXACT_PLUGING_NAME konnte REGEX_GROUP aktualisiert werden.
warn_details = EMAIL_SUBJECT_REGEX Das Wordpress Plugin EXACT_PLUGING_NAME konnte nicht REGEX_GROUP aktualisiert werden.
crit_details = EMAIL_SUBJECT_REGEX Das Wordpress Plugin EXACT_PLUGING_NAME konnte seit einer weile nicht REGEX_GROUP aktualisiert werden.
