[b'z' if foldnuls and not word else
              b'y' if foldspaces and word == 0x20202020 else
              (chars2[word // 614125] +
               chars2[word // 85 % 7225] +
               chars[word % 85])
]
