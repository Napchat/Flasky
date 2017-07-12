## 1. Why cannot send email when register and resend?
Do: It is connection problem. You need to use lantern.

## 2. How to establish one-to-many relationship?
Do: The elements in the 'many' side have a foreign key that points to the linked
    element on the 'one' side. and the elements in the 'one' side have a relationship
    key for backref.

## 3. How to establish many-to-many relationship?
Do: Decompose the many-to-many relationship into two one-to-many relationshios from
    each of the two original tables to the association table.

    ```
    registratitons = db.Table('registrations',
        db.Column(.....)
        db.Column(.....)
    )

    class Student(db.Model):
        id = db.Column(.....)
        name = db.Column(....)
        classes = db.relationship(
            'Class',
            secondary=registrations,
            backref=(db.backref('students', lazy='dynamic'),
            lazy='dynamic'
    )

    class Class(db.Model)
        id = db.Column(......)
        name = db.Column(....)

    ```