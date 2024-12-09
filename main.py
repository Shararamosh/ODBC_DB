"""
    Connecting to database and creating department and employee tables.
    By default, T-SQL dialect and SQL Server LocalDB are used.
"""
from __future__ import annotations
import logging
import random
import textwrap
import pyodbc
from faker import Faker

Faker.seed(73)
fake = Faker("en_US")
DB_DRIVER = "ODBC Driver 18 for SQL Server" # Driver for connecting to database.
DB_SERVER = r"(localdb)\MSSQLLocalDB" # Database server.
DB_DATABASE = "ODBC_DB" # Database name.
conn = pyodbc.connect(f"DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE}")
cursor = conn.cursor()


class Department:
    """
    Class containing Department table fields.
    """

    def __init__(self, name: str):
        """
        Creates Department instance.
        :param name: Department name (limited to 100 characters).
        """
        self.name = textwrap.shorten(name, 100, placeholder="")
        self.id = None
        self.save()

    @classmethod
    def create_table(cls):
        """
        Creates department table.
        """
        sql = """
            CREATE TABLE department(
            id INTEGER PRIMARY KEY IDENTITY,
            name NVARCHAR(100) NOT NULL)
        """
        cursor.execute(sql)
        conn.commit()

    @classmethod
    def drop_table(cls):
        """
        Drops department table.
        """
        sql = """
            DROP TABLE department
        """
        cursor.execute(sql)
        conn.commit()

    def save(self):
        """
        Updating or inserting Department record into the department table.
        """
        if self.id is None:
            sql = """
                INSERT INTO department(name)
                VALUES (?)
            """
            cursor.execute(sql, self.name)
            cursor.execute("SELECT @@IDENTITY AS ID")
            self.id = cursor.fetchone()[0]
        else:
            sql = """
                UPDATE department
                SET name = ?
                WHERE id = ?
            """
            cursor.execute(sql, self.name, self.id)
        conn.commit()


class Employee:
    """
    Class containing Employee table fields.
    """

    def __init__(self, department: Department, chief: Employee | None, name: str, salary: int):
        """
        Creates Employee instance.
        :param department: Department instance Employee belongs to.
        :param chief: Employee instance that rules this Employee.
        :param name: Employee name (limited to 100 characters).
        :param salary: Employee salary.
        """
        self.department = department
        self.chief = chief
        self.name = textwrap.shorten(name, 100, placeholder="")
        self.salary = salary
        self.id = None
        self.save()

    @classmethod
    def create_table(cls):
        """
        Creates employee table.
        """
        sql = """
            CREATE TABLE employee(
            id INTEGER PRIMARY KEY IDENTITY,
            department_id INTEGER NOT NULL,
            chief_id INTEGER,
            name NVARCHAR(100) NOT NULL,
            SALARY INTEGER NOT NULL,
            FOREIGN KEY (department_id) REFERENCES department(id),
            FOREIGN KEY (chief_id) REFERENCES employee(id))
        """
        cursor.execute(sql)
        conn.commit()

    @classmethod
    def drop_table(cls):
        """
        Drops employee table.
        """
        sql = """
            DROP TABLE employee
        """
        cursor.execute(sql)
        conn.commit()

    def save(self):
        """
        Updating or inserting Employee record into the employee table.
        """
        if self.id is None:
            sql = """
                INSERT INTO employee(department_id, chief_id, name, salary)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(sql, self.department.id,
                           self.chief.id if self.chief is not None else None, self.name,
                           self.salary)
            cursor.execute("SELECT @@IDENTITY AS ID")
            self.id = cursor.fetchone()[0]
        else:
            sql = """
                UPDATE employee
                SET department_id = ?, chief_id = ?, name = ?, salary = ?
                WHERE id = ?
            """
            cursor.execute(sql, self.department.id,
                           self.chief.id if self.chief is not None else None,
                           self.name, self.salary, self.id)
        conn.commit()


def create_tables():
    """
    Drops existing Employee and Department tables and creates new ones.
    """
    try:
        Employee.drop_table()
    except Exception as e:
        logging.warning(e)
    try:
        Department.drop_table()
    except Exception as e:
        logging.warning(e)
    Department.create_table()
    Employee.create_table()


def get_random_departments(amount: int) -> list[Department]:
    """
    Creates list of fake Department objects.
    :param amount: Amount of Departments.
    :return: List of Departments.
    """
    departments = []
    for _ in range(amount):
        department = Department(fake.unique.catch_phrase())
        departments.append(department)
    return departments


def get_random_employees(amount: int, departments: list[Department]) -> list[Employee]:
    """
    Creates list of fake Employee objects.
    :param amount: Amount of Employees.
    :param departments: List of Department.
    :return: List of Employees.
    """
    employees = []
    if len(departments) < 1:
        return employees
    for _ in range(amount):
        department_pos = random.randint(0, len(departments) - 1)
        if len(employees) > 0:
            chief_pos = random.randint(-1, len(employees) - 1)
        else:
            chief_pos = -1
        employee = Employee(departments[department_pos],
                            employees[chief_pos] if chief_pos > -1 else None, fake.unique.name(),
                            random.randint(20000, 100001))
        employees.append(employee)
    return employees


def create_fake_data(departments_amount: int, employees_amount: int) -> (
        list[Department], list[Employee]):
    """
    Creates fake data about Departments and Employees.
    :param departments_amount: Amount of Departments.
    :param employees_amount: Amount of Employees.
    :return: Tuple of Departments list and Employees list.
    """
    departments = get_random_departments(departments_amount)
    employees = get_random_employees(employees_amount, departments)
    return departments, employees


create_tables()
create_fake_data(random.randint(3, 10), random.randint(10, 50))
cursor.close()
conn.close()
