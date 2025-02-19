import os, sys
patchList = []

def combinePatches(patchList:list):
    with open('code_combined.ips', 'wb') as outF:
        outF.write(b'PATCH')
        for patch in patchList:
            with open(patch, 'rb') as f:
                data = f.read()
                data = data[5:len(data)-3]
                outF.write(data)
        outF.write(b"EOF")

if __name__ == "__main__":
    try:
        if len(sys.argv) <= 1: raise IndexError
        for args in sys.argv[1:]: patchList.append(args)
    except IndexError:
        print(f"Usage:\n py {os.path.basename(__file__)} [patch1] [patch2] [patch3] [patch4] [etc]\n\nThe application takes as many args as you have patches.\nDoes not work with just one patch, obviously...")
        sys.exit(1)

    combinePatches(patchList)
