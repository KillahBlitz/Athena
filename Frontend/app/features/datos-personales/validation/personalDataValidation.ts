export interface ValidationErrors {
  name?: string
  email?: string
  age?: string
  avatar?: string
  area?: string
  terms?: string
}

export function validatePersonalData(form: {
  name: string
  email: string
  age: number | null
  selectedAvatarId: string | null
  selectedAreaId: number | null
  termsAccepted: boolean
}): { isValid: boolean; errors: ValidationErrors } {
  const errors: ValidationErrors = {}

  if (!form.name || form.name.trim().length === 0) {
    errors.name = 'El nombre es obligatorio.'
  } else if (form.name.trim().length < 2) {
    errors.name = 'Por favor ingresa un nombre válido.'
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!form.email || form.email.trim().length === 0) {
    errors.email = 'El correo electrónico es obligatorio.'
  } else if (!emailRegex.test(form.email.trim())) {
    errors.email = 'Ingresa un correo electrónico con formato válido (ej. usuario@correo.com).'
  }

  const ageNum = Number(form.age)
  if (form.age === null || Number.isNaN(ageNum) || String(form.age).trim() === '') {
    errors.age = 'La edad es obligatoria.'
  } else if (ageNum < 12 || ageNum > 100) {
    errors.age = 'Ingresa una edad válida (entre 12 y 100 años).'
  }

  if (!form.selectedAvatarId) {
    errors.avatar = 'Selecciona un avatar para acompañarte.'
  }

  if (form.selectedAreaId === null) {
    errors.area = 'Selecciona un área académica para comenzar la exploración.'
  }

  if (!form.termsAccepted) {
    errors.terms = 'Debes aceptar los términos y condiciones para continuar.'
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  }
}
