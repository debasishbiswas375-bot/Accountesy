import { useState, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { useToast } from '@/components/ui/toast'
import { Eye, EyeOff, User, Mail, Phone, MapPin, Building, Check, RefreshCcw } from 'lucide-react'
import { supabase } from '@/lib/supabase'

// ---------------- TYPES ----------------
interface FormData {
  username: string
  full_name: string
  email: string
  contact_number: string
  address_line: string
  pincode: string
  district: string
  state: string
  country: string
  password: string
  confirm_password: string
  company_name: string
  captcha_input: string
}

const initialForm: FormData = {
  username: '',
  full_name: '',
  email: '',
  contact_number: '',
  address_line: '',
  pincode: '',
  district: '',
  state: '',
  country: '',
  password: '',
  confirm_password: '',
  company_name: '',
  captcha_input: '',
}

// ---------------- CAPTCHA ----------------
function generateCaptcha() {
  const a = Math.floor(Math.random() * 20) + 1
  const b = Math.floor(Math.random() * 20) + 1
  return { question: `${a} + ${b} = ?`, answer: String(a + b) }
}

// ---------------- COMPONENT ----------------
export function Register() {
  const [form, setForm] = useState<FormData>(initialForm)
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [captcha, setCaptcha] = useState(generateCaptcha()) // ✅ FIXED
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({})

  const { addToast } = useToast()
  const navigate = useNavigate()

  // ---------------- UPDATE FIELD ----------------
  const updateField = useCallback((field: keyof FormData, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }))
    setErrors(prev => ({ ...prev, [field]: undefined }))
  }, [])

  // ---------------- PINCODE AUTO FETCH ----------------
  const handlePincodeChange = async (value: string) => {
    updateField('pincode', value)

    if (value.length !== 6) return

    try {
      const res = await fetch(`https://api.postalpincode.in/pincode/${value}`)
      const data = await res.json()

      if (data[0].Status === "Success") {
        const post = data[0].PostOffice[0]

        setForm(prev => ({
          ...prev,
          district: post.District,
          state: post.State,
          country: post.Country
        }))
      }
    } catch {
      console.log("Pincode fetch failed")
    }
  }

  // ---------------- VALIDATION ----------------
  const validate = (): boolean => {
    const errs: Partial<Record<keyof FormData, string>> = {}

    if (form.username.trim().length < 6) errs.username = 'Min 6 chars'
    if (!form.full_name.trim()) errs.full_name = 'Required'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errs.email = 'Invalid email'
    if (!form.contact_number.trim()) errs.contact_number = 'Required'
    if (form.password.length < 6) errs.password = 'Min 6 chars'
    if (form.password !== form.confirm_password) errs.confirm_password = 'Mismatch'
    if (form.captcha_input !== captcha.answer) errs.captcha_input = 'Wrong answer'

    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  // ---------------- SUBMIT ----------------
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)

    try {
      // 🔐 Supabase signup
      const { data, error } = await supabase.auth.signUp({
        email: form.email,
        password: form.password
      })

      if (error) throw error

      // 🧾 Insert extra user data
      await supabase.from('users').insert({
        id: data.user?.id,
        email: form.email,
        username: form.username,
        phone: form.contact_number,
        address1: form.address_line,
        pincode: form.pincode,
        district: form.district,
        state: form.state,
        country: form.country
      })

      addToast({
        title: 'Signup successful! Check your email.',
        variant: 'success'
      })

      navigate('/login')

    } catch (err: any) {
      addToast({
        title: err.message || 'Signup failed',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  // ---------------- UI ----------------
  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4 py-8">
      <div className="w-full max-w-xl">
        <Card>
          <CardHeader className="text-center">
            <CardTitle>Create Account</CardTitle>
            <CardDescription>Register using your email</CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-3">

              <Input placeholder="Username" value={form.username} onChange={e => updateField('username', e.target.value)} />
              <Input placeholder="Full Name" value={form.full_name} onChange={e => updateField('full_name', e.target.value)} />
              <Input type="email" placeholder="Email" value={form.email} onChange={e => updateField('email', e.target.value)} />
              <Input placeholder="Contact Number" value={form.contact_number} onChange={e => updateField('contact_number', e.target.value)} />
              <Input placeholder="Address" value={form.address_line} onChange={e => updateField('address_line', e.target.value)} />

              <Input placeholder="Pincode" value={form.pincode} onChange={e => handlePincodeChange(e.target.value)} />
              <Input placeholder="District" value={form.district} readOnly />
              <Input placeholder="State" value={form.state} readOnly />
              <Input placeholder="Country" value={form.country} readOnly />

              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Password"
                  value={form.password}
                  onChange={e => updateField('password', e.target.value)}
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)}>
                  {showPassword ? <EyeOff /> : <Eye />}
                </button>
              </div>

              <Input
                type="password"
                placeholder="Confirm Password"
                value={form.confirm_password}
                onChange={e => updateField('confirm_password', e.target.value)}
              />

              <Input placeholder="Company Name" value={form.company_name} onChange={e => updateField('company_name', e.target.value)} />

              <div>
                <p>{captcha.question}</p>
                <div className="flex gap-2">
                  <Input
                    placeholder="Answer"
                    value={form.captcha_input}
                    onChange={e => updateField('captcha_input', e.target.value)}
                  />
                  <button type="button" onClick={() => setCaptcha(generateCaptcha())}>
                    <RefreshCcw />
                  </button>
                </div>
              </div>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Creating...' : 'Create Account'}
              </Button>

              <p className="text-center text-sm">
                Already have account? <Link to="/login">Login</Link>
              </p>

            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
