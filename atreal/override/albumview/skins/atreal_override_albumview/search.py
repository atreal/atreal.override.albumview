#

request = context.REQUEST
query_string = ""

if request.environ.has_key('QUERY_STRING'):
    query_string = "?"+request.environ['QUERY_STRING']

request.RESPONSE.redirect(context.portal_url() + '/@@search%s' % query_string)
