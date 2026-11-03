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

  const name = (form.name || '').trim()
  if (!name || name.length === 0) {
    errors.name = 'El nombre es obligatorio.'
  } else if (name.length < 3) {
    errors.name = 'El nombre debe tener al menos 3 caracteres.'
  } else if (name.length > 100) {
    errors.name = 'El nombre no puede exceder los 100 caracteres.'
  } else if (!/[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]/.test(name) || /^[\d\s]+$/.test(name)) {
    errors.name = 'El nombre no puede estar compuesto únicamente por números.'
  }

  const email = (form.email || '').trim()
  const emailParts = email.split('@')
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  if (!email || email.length === 0) {
    errors.email = 'El correo electrónico es obligatorio.'
  } else if (email.length > 254) {
    errors.email = 'El correo no puede exceder los 254 caracteres en total.'
  } else if (emailParts.length > 2) {
    errors.email = 'El correo no puede contener más de un @.'
  } else if (emailParts.length < 2) {
    errors.email = 'Ingresa un correo electrónico con formato válido (ej. usuario@correo.com).'
  } else if ((emailParts[0]?.length ?? 0) > 64) {
    errors.email = 'El correo no puede tener más de 64 caracteres antes del @.'
  } else if ((emailParts[0]?.length ?? 0) === 0 || !emailRegex.test(email)) {
    errors.email = 'Ingresa un correo electrónico con formato válido (ej. usuario@correo.com).'
  }

  const ageNum = Number(form.age)
  if (form.age === null || Number.isNaN(ageNum) || String(form.age).trim() === '') {
    errors.age = 'La edad es obligatoria.'
  } else if (!Number.isInteger(ageNum) || ageNum < 13 || ageNum > 45) {
    errors.age = 'Ingresa una edad válida (entre 13 y 45 años).'
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
