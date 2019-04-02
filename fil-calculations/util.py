# http://code.activestate.com/recipes/577081-humanized-representation-of-a-number-of-bytes/ | MIT License
def humanize_bytes(bytes, precision=1):
    """Return a humanized string representation of a number of bytes.

    >>> humanize_bytes(1)
    '1 byte'
    >>> humanize_bytes(1024)
    '1.0 KiB'
    >>> humanize_bytes(1024*123)
    '123.0 KiB'
    >>> humanize_bytes(1024*12342)
    '12.1 MiB'
    >>> humanize_bytes(1024*12342,2)
    '12.05 MiB'
    >>> humanize_bytes(1024*1234,2)
    '1.21 MiB'
    >>> humanize_bytes(1024*1234*1111,2)
    '1.31 GiB'
    >>> humanize_bytes(1024*1234*1111,1)
    '1.3 GiB'
    """
    abbrevs = (
        (1<<50, 'PiB'),
        (1<<40, 'TiB'),
        (1<<30, 'GiB'),
        (1<<20, 'MiB'),
        (1<<10, 'KiB'),
        (1, 'bytes')
    )
    if bytes == 1:
        return '1 byte'
    for factor, suffix in abbrevs:
        if bytes >= factor:
            break
    return '%.*f %s' % (precision, bytes / factor, suffix)

def humanize_seconds(seconds, precision=1):
    """Return a humanized string representation of a number of seconds.
    """

    minute = 60
    hour = minute * 60

    hours = seconds  // hour
    minutes = (seconds % hour) // minute
    seconds = seconds % minute

    return ('-' if (seconds < 0) else '') + '%02d:%02d:%.*f' % (hours, minutes, precision, seconds)
