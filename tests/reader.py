import os, sys, threading, time, hashlib

# reader.py slowly read a file and verifies that the file read matches on of the
# predefined checksums
# It expects a file named "file" in the current directory and will keep reading this file.
#
# The purpose of this script is to verify behaviour when a file is being updated while it is being read.
# Safe file update example:
# $ cp file1 file1.tmp; mv file1.tmp file
# Unsafe example:
# $ cp file1 file

# Files can be generated using:
# $ dd bs=1024 count=1024 if=/dev/urandom of=file1
# $ dd bs=1024 count=1024 if=/dev/urandom of=file2
# Then:
# shasum file1; shasum file2
# Put calculated SHA-1 checksum in test_files_sha1 below

test_files_sha1 = ( '3926c59c7ed147f25e798ebac377512560990ebc', '07d61ae9bc49ddb9d68719043efbbc8295c3ff6d' )

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
