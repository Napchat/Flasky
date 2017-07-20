## 1. Why cannot send email when register and resend?
Answer: It is connection problem. You need to use lantern.

## 2. How to establish one-to-many relationship?
Answer: The elements in the 'many' side have a foreign key that points to the linked
    element on the 'one' side. and the elements in the 'one' side have a relationship
    key for backref.

## 3. How to establish many-to-many relationship?
Answer: Decompose the many-to-many relationship into two one-to-many relationshios from
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

## 4. Why is there no change when I modified some files before pushing to heroku?
Answer: If you changed your file before pushing to heroku, execute `git add` and `git commit` first.

## 5. Heroku internal server error?
Answer: you need to specify the heroku database_url.