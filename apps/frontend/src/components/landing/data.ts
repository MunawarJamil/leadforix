export const HERO = {
  badge: 'Built for developers',
  headlineLead: 'Your next tech role,',
  headlineGradient: 'found and ranked for you.',
  subtext:
    'Fresh openings scanned daily, duplicates removed, every role scored against your skills — so you only see what actually fits.',
  ctaPrimary: 'Create Free Profile',
  ctaSecondary: 'Sign In',
  ctaTertiary: 'Upload resume',
} as const

export const STATS = [
  'Fresh leads daily',
  'Ranked by match',
  'Zero duplicates',
] as const

// Edit this array when you audit what your sources actually return.
export const TECH_TAGS = [
  'React',
  'TypeScript',
  'Node.js',
  'Python',
  'Go',
  'Rust',
  'DevOps',
  'Kubernetes',
  'AWS',
  'PostgreSQL',
  'GraphQL',
  'Next.js',
  'Vue',
  'Django',
  'FastAPI',
  'Docker',
  'Terraform',
  'ML / AI',
  'Swift',
  'Kotlin',
] as const

export const STEPS = [
  {
    title: 'Build your profile',
    body: 'Tell us your stack, seniority, and what you want next. Takes two minutes.',
  },
  {
    title: 'We find and score',
    body: 'Fresh roles land daily, duplicates get dropped, and each one is scored against your skills.',
  },
  {
    title: 'You pick and reach out',
    body: 'See only the roles worth your time, ranked by match. Reach out when you are ready.',
  },
] as const

// Gate these once you confirm what your sources return.
export const ROLES = [
  'Frontend',
  'Backend',
  'Full-stack',
  'DevOps',
  'Mobile',
  'Data / AI',
] as const

export const MORE_ROLES_LABEL = 'More tech roles soon'

export const FAQ = [
  {
    q: 'Is Leadforix free to use?',
    a: 'Yes. Creating a profile and browsing ranked leads is free. You only pay if you choose to upgrade for advanced filters or outreach tools.',
  },
  {
    q: 'How fresh is the data?',
    a: 'New roles are scanned and added daily. Duplicates are removed automatically before anything reaches your feed, so what you see is what is actually open.',
  },
  {
    q: 'What happens to my resume?',
    a: 'Your resume is used only to score roles against your skills. It is never sold, never shared with employers without your say-so, and you can delete it any time from your profile.',
  },
] as const

// Demo cards for hero preview + live demo section
export const SAMPLE_LEADS = [
  {
    id: 'l1',
    role: 'Senior Frontend Engineer',
    company: 'Northwind',
    location: 'Remote · EU',
    tags: ['React', 'TypeScript', 'GraphQL'],
    score: 94,
  },
  {
    id: 'l2',
    role: 'Backend Engineer, Platform',
    company: 'Ionis Labs',
    location: 'Hybrid · Berlin',
    tags: ['Go', 'PostgreSQL', 'Kubernetes'],
    score: 87,
  },
  {
    id: 'l3',
    role: 'Full-stack Developer',
    company: 'Kestrel',
    location: 'Remote · Global',
    tags: ['Node.js', 'Next.js', 'AWS'],
    score: 81,
  },
] as const