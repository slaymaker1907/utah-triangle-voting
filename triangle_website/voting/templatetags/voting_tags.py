from django import template

register = template.Library()

# This is just a simple dictionary lookup. If the key is not present,
# returns the default value (usually None).
@register.filter
def dict_get(dict, key):
	return dict.get(key)