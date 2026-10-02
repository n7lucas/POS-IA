# services/appointment_service.py
from typing import Optional, List
from models import Professional, Appointment

class AppointmentService:
    def __init__(self):
        # Mocks em memória
        self._professionals: List[Professional] = [
            Professional(id=1, name="Dr. Alicio da Silva", specialty="Cardiologia"),
            Professional(id=2, name="Dra. Ana Pereira", specialty="Dermatologia"),
            Professional(id=3, name="Dra. Carol Gomes", specialty="Neurologia"),
        ]
        self._appointments: List[Appointment] = [
            Appointment(
                id=1,
                professional_id=1,
                date_time="2026-10-10T10:00:00",
                patient_name="Erick",
                reason="Checkup de rotina"
            )
        ]

    def get_professionals(self) -> List[Professional]:
        return self._professionals

    def find_professional_by_id(self, prof_id: int) -> Optional[Professional]:
        return next((p for p in self._professionals if p.id == prof_id), None)

    def book(
        self, 
        professional_id: int, 
        date_time: str, 
        patient_name: str, 
        reason: Optional[str] = None
    ) -> Appointment:
        """Tenta agendar uma consulta. Lança ValueError se o horário estiver ocupado."""
        # Checa duplicidade/conflito de horário para o mesmo profissional
        for app in self._appointments:
            if app.professional_id == professional_id and app.date_time == date_time:
                raise ValueError(f"O horário {date_time} já está ocupado para este profissional.")

        new_id = len(self._appointments) + 1
        new_appointment = Appointment(
            id=new_id,
            professional_id=professional_id,
            date_time=date_time,
            patient_name=patient_name,
            reason=reason or "Consulta Geral"
        )
        self._appointments.append(new_appointment)
        return new_appointment

    def cancel(self, professional_id: int, patient_name: str, date_time: str) -> bool:
        """Cancela uma consulta existente. Lança ValueError se não encontrar."""
        for idx, app in enumerate(self._appointments):
            if (
                app.professional_id == professional_id 
                and app.patient_name.lower() == patient_name.lower()
                and app.date_time == date_time
            ):
                del self._appointments[idx]
                return True
        
        raise ValueError(f"Nenhuma consulta encontrada para {patient_name} com o profissional no horário informado.")
        