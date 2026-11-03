export interface AvatarTheme {
  primary: string
  soft: string
  border: string
  dark: string
  contrast: string
}

export interface Avatar {
  id: string
  name: string
  role: string
  image: string
  greeting: string
  encouragement: string
  color: string
  theme: AvatarTheme
}
