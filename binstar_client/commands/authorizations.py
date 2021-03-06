'''
Manage Authentication tokens
'''
from datetime import datetime
from binstar_client.utils import get_binstar
import getpass
from dateutil.parser import parse as parse_date
import sys
import pytz

def utcnow():
    now = datetime.utcnow()
    return now.replace(tzinfo=pytz.utc)

def format_timedelta(date):
    if not date:
        return 'Never'
    
    now = utcnow()
    
    if date < utcnow():
        return  'expired'

    delta = date - now

    if delta.days:
        days = (delta.days + (delta.seconds / (60. * 60. * 24.0)))
        if days > 3:
            days = int(days)
            return '%i days' % days
        else:
            return '%.1f days' % days
    elif delta.seconds > 60 * 60:
        return  '%.1f hours' % (delta.seconds / (60. * 60))
    elif delta.seconds > 60:
        return '%i minutes' % (delta.seconds // 60)
    else:
        return '%i seconds' % delta.seconds


def show_auths(authentications):
    header = {'id': 'ID', 'application': 'Application',
              'remote_addr':'Remote Addr',
              'hostname':'Host',
              'expires':'Expires In'}

    template = '%(id)-25s | %(application)-20s | %(remote_addr)-20s | %(hostname)-20s | %(expires)-20s'
    print
    print template % header
    print '%s-+-%s-+-%s-+-%s-+-%s' % ('-' * 25, '-' * 20, '-' * 20, '-' * 20, '-' * 20)

    for auth in authentications:
        if auth['expires']:
            expires = parse_date(auth['expires'])
        else:
            expires = None
        auth['expires'] = format_timedelta(expires)

        print template % auth


def main(args):
    binstar = get_binstar(args)
    if args.list:
        show_auths(binstar.authentications())
        return
    elif args.remove:
        for auth_id in args.remove:
            binstar.remove_authentication(auth_id)
        return
    elif args.list_scopes:
        scopes = binstar.list_scopes()
        for key in sorted(scopes):
            print key
            print ' ', scopes[key]
            print
            
    elif args.create:

        sys.stderr.write('Username: ')
        sys.stderr.flush()
        username = raw_input('')
        password = getpass.getpass()
        
        scopes = [scope for scopes in args.scopes for scope in scopes.split()]
        print binstar.authenticate(username, password,
                                   args.name, application_url=args.url,
                                   scopes=scopes,
                                   for_user=args.user,
                                   max_age=args.max_age,
                                   created_with=' '.join(sys.argv))



def add_parser(subparsers):

    parser = subparsers.add_parser('auth',
                                    help='Manage Authorization Tokens',
                                    description=__doc__)
    parser.add_argument('-n', '--name', default='Binstar Cli', help='The name of the application that will use this token')
    parser.add_argument('--url', default='http://binstar.org', help='The url of the application that will use this token')
    parser.add_argument('--max-age', type=int, help='The maximum age in seconds that this token will be valid for')
    parser.add_argument('--resource', default='api:**', help='The resource path that this token is valid')
    parser.add_argument('-s', '--scopes', action='append', help='Scopes for token', default=[])
    parser.add_argument('-u', '--user', help='Set the token owner (may be an organization)')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-x', '--list-scopes', action='store_true', help='list all authentication scopes')
    group.add_argument('-l', '--list', action='store_true', help='list all user authentication tokens')
    group.add_argument('-r', '--remove', metavar='ID', nargs='+', help='remove authentication tokens')
    group.add_argument('-c', '--create', action='store_true', help='Create an authentication token')
    parser.set_defaults(main=main)



