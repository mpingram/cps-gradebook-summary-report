from create_gradebook_summary import create_gradebook_summary

if __name__ == "__main__":
    teacher_fullname_list = [
            "Luz Escobar",
            "Maria DeSanto",
            "Lorena Velasco",
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

    for teacher in teacher_fullname_list:
        print("Printing gradebook summary for {}...".format(teacher))
        create_gradebook_summary(teacher)
        print("Done!")

