[Service]

# To adapt this template to any Wordpress Plugin replace EXACT_PLUGING_NAME
#     with the name that it has in the update mails (without spaces at the beginning or end)

# Any Regex is defined without "" even if syntax highlighting looks weird

# This defines the regex that looks at the email subject lines
#   if it matches to anything but nothing a service file is created with details
#   from the following options
email_subject_regex = (\[.+\]) Einige Plugins

# This defines the service name that will appear in CheckMk
# EMAIL_SUBJECT_REGEX will be replaced by the match group from email_subject_regex
name = EMAIL_SUBJECT_REGEX Wordpress Plugin EXACT_PLUGING_NAME

# These define the RegEx that will check the email body for their respective statuses
ok_regex = neuesten Stand:\n- (?:.*\n- )*EXACT_PLUGING_NAME \((.+)\)
warn_regex = nicht aktualisiert werden:\n- (?:.*\n- )*EXACT_PLUGING_NAME \((.+)\)
# crit_regex = your regex which matches to the email body which conveys a critical status here

# This defines how many hours must pass without any new email before the status is set to WARN
warn_cycle = 24 
# This defines how many hours must pass without any new email before the status is set to CRIT
crit_cycle = 48

# For the status types warn and crit either a regex or a cycle must be defined 
# Any other option must always be defined

# These define what should be in the service details that are sent to CheckMk
# REGEX_GROUP will be replaced with the capture group from the respective RegEx
#     if you want to provide more details like the version number in this case
#     if the status warn was reached by warn_regex the capture group from warn_regex will be used
#     but if the status warn was reached with warn_cycle the capture group from a lower level will be used e.g. the
#     capture group from ok_regex
ok_details = EMAIL_SUBJECT_REGEX Das Wordpress Plugin EXACT_PLUGING_NAME konnte REGEX_GROUP aktualisiert werden.
warn_details = EMAIL_SUBJECT_REGEX Das Wordpress Plugin EXACT_PLUGING_NAME konnte nicht REGEX_GROUP aktualisiert werden.
crit_details = EMAIL_SUBJECT_REGEX Das Wordpress Plugin EXACT_PLUGING_NAME konnte seit einer weile nicht REGEX_GROUP aktualisiert werden.
