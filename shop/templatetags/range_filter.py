from django import template

register = template.Library()

@register.filter
def range_filter(value):
    return range(2, int(value)+1 )

@register.filter
def star_filter(rating):
    stars = []
    for i in range(1, 6):  # 1 to 5 stars
        if rating >= i:
            stars.append('full')  # Full star
        elif rating >= i - 0.5:
            stars.append('half')  # Half star
        else:
            stars.append('empty')  # Empty star
    return stars

@register.filter
def multiply(value1, value2):
    return value1 * value2