hcaps={}

hcaps.update({'P' : {'P' : [0, 9], 'O+' : [-2, 10],  'O' : [-3, 10], 'A+' : [-3, 9],
                     'A' : [-4, 10], 'B+' : [-5, 10],  'B' : [-6, 11],  'C+' : [-6, 10],
                     'C' : [-8, 11], 'D+' : [-8, 10], 'D' : [-9, 11]}})

hcaps.update({'O+' : {'P' : [2, 10], 'O+' : [0, 9],  'O' : [-1, 9], 'A+' : [-2, 9],
                      'A' : [-3, 10], 'B+' : [-4, 9],  'B' : [-5, 10],  'C+' : [-6, 11],
                      'C' : [-7, 11], 'D+' : [-7, 10], 'D' : [-8, 10]}})

hcaps.update({'O' : {'P' : [3, 10], 'O+' : [1, 9],  'O' : [0, 9], 'A+' : [-1, 9],
                     'A' : [-2, 8], 'B+' : [-3, 8],  'B' : [-4, 9],  'C+' : [-5, 10],
                     'C' : [-6, 11], 'D+' : [-7, 11], 'D' : [-7, 10]}})

hcaps.update({'A+' : {'P' : [3, 9], 'O+' : [2, 9],  'O' : [1, 9], 'A+' : [0, 8],
                      'A' : [-1, 8], 'B+' : [-2, 8],  'B' : [-3, 8],  'C+' : [-4, 9],
                      'C' : [-5, 10], 'D+' : [-6, 11], 'D' : [-7, 11]}})

hcaps.update({'A' : {'P' : [4, 10], 'O+' : [3, 10],  'O' : [2, 8], 'A+' : [1, 8],
                     'A' : [0, 8], 'B+' : [-1, 8],  'B' : [-2, 8],  'C+' : [-3, 8],
                     'C' : [-4, 9], 'D+' : [-5, 10], 'D' : [-6, 11]}})

hcaps.update({'B+' : {'P' : [5, 10], 'O+' : [4, 9],  'O' : [3, 8], 'A+' : [2, 8],
                      'A' : [1, 8], 'B+' : [0, 7],  'B' : [-1, 7],  'C+' : [-2, 7],
                      'C' : [-3, 8], 'D+' : [-4, 9], 'D' : [-5, 10]}})

hcaps.update({'B' : {'P' : [6, 11], 'O+' : [5, 10],  'O' : [4, 9], 'A+' : [3, 8],
                     'A' : [2, 8], 'B+' : [1, 7],  'B' : [0, 7],  'C+' : [-1, 7],
                     'C' : [-2, 7], 'D+' : [-3, 8], 'D' : [-4, 9]}})

hcaps.update({'C+' : {'P' : [6, 10], 'O+' : [6, 11],  'O' : [5, 10], 'A+' : [4, 9],
                      'A' : [3, 8], 'B+' : [2, 7],  'B' : [1, 7],  'C+' : [0, 7],
                      'C' : [-1, 7], 'D+' : [-2, 7], 'D' : [-3, 8]}})

hcaps.update({'C' : {'P' : [8, 11], 'O+' : [7, 11],  'O' : [6, 11], 'A+' : [5, 10],
                     'A' : [4, 9], 'B+' : [3, 8],  'B' : [2, 7],  'C+' : [1, 7],
                     'C' : [0, 7], 'D+' : [-1, 7], 'D' : [-2, 7]}})

hcaps.update({'D+' : {'P' : [8, 10], 'O+' : [7, 10],  'O' : [7, 11], 'A+' : [6, 11],
                      'A' : [5, 10], 'B+' : [4, 9],  'B' : [3, 8],  'C+' : [2, 7],
                      'C' : [1, 7], 'D+' : [0, 7], 'D' : [-1, 7]}})

hcaps.update({'D' : {'P' : [9, 11], 'O+' : [8, 10],  'O' : [7, 10], 'A+' : [7, 11],
                     'A' : [6, 11], 'B+' : [5, 10],  'B' : [4, 9],  'C+' : [3, 8],
                     'C' : [2, 7], 'D+' : [1, 7], 'D' : [0, 7]}})

ranks=[('P',  'Pro'),
       ('O+', 'Open +'),
       ('O',  'Open'),
       ('A+', 'A+'),
       ('A',  'A'),
       ('B+', 'B+'),
       ('B',  'B'),
       ('C+', 'C+'),
       ('C',  'C'),
       ('D+', 'D+'),
       ('D',  'D')]