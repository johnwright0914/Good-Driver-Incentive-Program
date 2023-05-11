from django import template

register = template.Library()
# this is a small template help function to 
# check the group assosicated with the user
@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
