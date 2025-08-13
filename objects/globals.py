class Global:
    REFERENCE_DICT = {}
    MIN_HEADLINE_LEVEL = 100

    @staticmethod
    def clear():
        Global.REFERENCE_DICT = {}
        Global.MIN_HEADLINE_LEVEL = 100

    @staticmethod
    def check():
        print("\nGlobal")
        print(f"REFERENCE_DICT = {Global.REFERENCE_DICT}")
        print(f"MIN_HEADLINE_LEVEL = {Global.MIN_HEADLINE_LEVEL}")
