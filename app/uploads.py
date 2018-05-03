from hashlib import md5


def filename_hash(name, email):
    """Return a file name that's the hash of a given email address"""

    extension = name.rsplit('.', 1)[1]
    email_hash = md5(email.lower().encode('utf-8')).hexdigest()
    return email_hash + '.' + extension
