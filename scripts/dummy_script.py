import time
import sys

def main():
    print("Dummy script started.", flush=True)
    try:
        count = 0
        while True:
            print(f"Working... {count}", flush=True)
            time.sleep(2)
            count += 1
    except KeyboardInterrupt:
        print("Dummy script stopped gracefully.", flush=True)
        sys.exit(0)

if __name__ == "__main__":
    main()
