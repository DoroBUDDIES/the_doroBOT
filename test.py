from thread_func import TimerThread, CameraThread

def main():
    print("Starting thread")
    c_thread = CameraThread()
    t_thread = TimerThread(seconds = 10)
    try:
        while(True):
            if(t_thread.thread_func_stop):
                break

            if(not c_thread.face_detected):
                print("Face not detected")
            else:
                print("Face detected")


    except KeyboardInterrupt:
        pass
    finally:
        t_thread.stop()
        c_thread.stop()
        exit(0)
    
if __name__ == '__main__':
    main()