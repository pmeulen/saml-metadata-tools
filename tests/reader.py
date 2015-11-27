import os, sys, threading, time, hashlib

# Files generated using:
# $ dd bs=1024 count=1024 if=/dev/urandom of=file1
# Then
# shasum file1

data_ready = threading.Event()

class KeyboardPoller( threading.Thread ):
    def run( self ):
        global key_pressed
        ch = sys.stdin.read( 1 )
        key_pressed = ch
        data_ready.set()

print "Reading file, press ENTER to exit"

poller = KeyboardPoller()
poller.start()

test_files_sha1 = ( '3926c59c7ed147f25e798ebac377512560990ebc', '07d61ae9bc49ddb9d68719043efbbc8295c3ff6d' )

while not data_ready.isSet():
    try:
        print "Opening file"
        fd = os.open('file', os.O_RDONLY)
    except Exception as e:
        print e
        time.sleep(1)
        continue
    print 'Opened file; fd=%i' % fd
    try:
        sha1 = hashlib.sha1()
        while not data_ready.isSet():
            res=os.read(fd, 10240)
            if (res == ''):
                break
            sha1.update(res)
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.1)

        sha1sum = sha1.hexdigest()
        print "Done reading file; sha1=%s" % sha1sum
        if sha1sum in test_files_sha1:
            print "SHA-1 OK"
        else:
            print "SHA-1 ERROR"

    except Exception as e:
        print e.message
    finally:
        print "Closing file; fd=%i" % fd
        os.close( fd )
        fd = None
