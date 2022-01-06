count = 4049
intendedRange = count//50
multipleList = []
print(intendedRange)
for i in range(intendedRange+1):
    multipleList.append(i*50)

if 250 in multipleList:
    print('SO TRUE!!')


# next steps:
# problem: oauth functionality failing. need to figure out why


# libPath = f'generated/libraries/{username}'
#     # genrePath = f'generated/libraries/{username}'

#     libFile = Path(libPath)
#     # genreFile = Path(genrePath)
#     original_umask = os.umask(0)

#     if libFile.exists():
#         pass
#     else:
    # try:
    #     os.makedirs(libPath, mode=0o777)
    # finally:
    #     os.umask(original_umask)

    # if libFile.exists() and genreFile.exists():
    #     pass
    # elif libFile.exists() and not genreFile.exists():
    #     try:
    #         os.makedirs(genrePath, mode=0o777)
    #     finally:
    #         os.umask(original_umask)

    # elif not libFile.exists() and genreFile.exists():
    #     try:
    #         os.makedirs(libPath, mode=0o777)
    #     finally:
    #         os.umask(original_umask)
    # else:
    # try:
    #     os.makedirs(libPath, mode=0o777)
    # finally:
    #     os.umask(original_umask)
