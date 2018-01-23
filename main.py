import matplotlib
matplotlib.use('Agg')

from create_gradebook_summary import create_gradebook_summary

if __name__ == "__main__":

    teacher_fullname_list = [
            "Lorena Velasco",
            "Luz Escobar",
            "Maria DeSanto",
            "Beatriz Lopez",
            "Rebecca Reddicliffe",
           "Ana Cabrera",
            "Bethany Jorgensen",
            "Adriana Soto",
            "Mayra Velasco",
            "Liliana Martinez-Vargas",
            "Ashley McCall",
            "Lindsay Singer",
            "Tiffany Humphrey",
            "Daniel Kim",
            "Nancy Montoya",
            "Sara Strasser",
            "Jennie Vazquez",
            "Lacey Elliott",
            "Katelyn Bell",
            "Agnieszka Opacian",
            "Marcella Cadena",
            "Catherine Kompare",
            "Andrea Lancki",
            "Jaime McLaughlin",
            "Christopher Brekke",
            "Stacy Ambler",
            "Isidro Lopez",
            "Priscilla Centeno",
            "Litaysha Turner",
            "Mary Iverson"
        ]

    homeroom_list = [
       'B312', 'A303', 'A122AM', 'A306', 'A301', 'A206', 'A307', 'A121AM',             
       'B214', 'B314', 'A302', 'B316', 'B212', 'A207', 'B313', 'B211',                 
       'A201', 'A203', 'A308', 'A305', 'B317', 'A304', 'B318', 'B217',                 
       'A107', 'B213', 'A202', 'A309', 'B218', 'A208', 'A108', 'A205',                 
       'A122PM', 'B216', 'A101', 'A121PM', 'A102', 'A103', 'B115'
            ]

    for teacher in teacher_fullname_list:
        for homeroom in homeroom_list:
            success = create_gradebook_summary(teacher, homeroom)
            if success:
                print("Printed gradebook summary for {}-{}...".format(homeroom, teacher))

