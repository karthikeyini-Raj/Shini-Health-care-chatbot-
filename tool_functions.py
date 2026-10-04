import pyodbc


def get_connection():

    conn = pyodbc.connect(
        r"DRIVER={ODBC Driver 17 for SQL Server};"
        r"SERVER=.\DEVINSTANCE;"
        r"DATABASE=Superclinic;"
        r"Trusted_Connection=yes;"
    )

    return conn


def check_doctor_exists(doctor_name):

    conn = get_connection()

    cursor = conn.cursor()

    query = """
        SELECT DoctorID,
               FirstName,
               LastName,
               Department
        FROM Doctors
        WHERE FirstName LIKE ?
    """

    cursor.execute(query, f"%{doctor_name}%")

    doctor = cursor.fetchone()

    conn.close()

    return doctor


def get_doctor_by_department(department):

    conn = get_connection()

    cursor = conn.cursor()

    query = """
        SELECT TOP 1
               DoctorID,
               FirstName,
               LastName,
               Department
        FROM Doctors
        WHERE Department = ?
    """

    cursor.execute(query, department)

    doctor = cursor.fetchone()

    conn.close()

    return doctor

def create_patient(
    first_name,
    last_name,
    email,
    phone_number,
    city
    ):


    conn = get_connection()

    cursor = conn.cursor()

    query = """
        INSERT INTO Patients
        (
            FirstName,
            LastName,
            Email,
            PhoneNumber,
            City,
            JoinDate
        )
        VALUES (?, ?, ?, ?, ?, GETDATE())
    """

    cursor.execute(
        query,
        first_name,
        last_name,
        email,
        phone_number,
        city
    )

    conn.commit()

    # Get newly inserted patient
    cursor.execute("""
        SELECT TOP 1 PatientID
        FROM Patients
        ORDER BY PatientID DESC
    """)

    result = cursor.fetchone()

    conn.close()

    if result is not None:

        return result[0]

    return None

def book_appointment(
        patient_id,
        doctor_id,
        appointment_date,
        appointment_time,
        symptoms
):

    conn = get_connection()

    cursor = conn.cursor()

    query = """
        INSERT INTO Appointments
        (
            PatientID,
            DoctorID,
            AppointmentDate,
            AppointmentTime,
            Status,
            Symptoms
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        query,
        patient_id,
        doctor_id,
        appointment_date,
        appointment_time,
        "Booked",
        symptoms
    )

    conn.commit()

    conn.close()

    return "Appointment Booked Successfully"


def get_patient_by_phone(phone_number):

    conn = get_connection()

    cursor = conn.cursor()

    query = """
        SELECT *
        FROM Patients
        WHERE PhoneNumber = ?
    """

    cursor.execute(query, phone_number)

    patient = cursor.fetchone()

    conn.close()

    return patient

def is_slot_available(
        doctor_id,
        appointment_date,
        appointment_time
):

    conn = get_connection()

    cursor = conn.cursor()

    query = """
        SELECT *
        FROM Appointments
        WHERE DoctorID = ?
        AND AppointmentDate = ?
        AND AppointmentTime = ?
        AND Status = 'Booked'
    """

    cursor.execute(
        query,
        doctor_id,
        appointment_date,
        appointment_time
    )

    appointment = cursor.fetchone()

    conn.close()

    return appointment is None
def get_available_slots(doctor_id, appointment_date):

    all_slots = [
        "10:00 AM",
        "11:00 AM",
        "12:00 PM",
        "02:00 PM",
        "03:00 PM",
        "04:00 PM"
    ]

    conn = get_connection()

    cursor = conn.cursor()

    query = """
        SELECT AppointmentTime
        FROM Appointments
        WHERE DoctorID = ?
        AND AppointmentDate = ?
        AND Status = 'Booked'
    """

    cursor.execute(query, doctor_id, appointment_date)

    booked_slots = [row[0] for row in cursor.fetchall()]

    conn.close()

    available_slots = [
        slot for slot in all_slots
        if slot not in booked_slots
    ]

    return available_slots