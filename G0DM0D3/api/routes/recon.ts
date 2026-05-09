import { Router } from 'express'
import axios from 'axios'

export const reconRoutes = Router()

const RECON_API_BASE = process.env.RECON_API_URL || 'http://localhost:8000'

/**
 * Start a reconnaissance mission
 * POST /v1/recon/start
 */
reconRoutes.post('/start', async (req, res) => {
  try {
    const { target } = req.body
    if (!target) {
      return res.status(400).json({ error: 'target is required' })
    }

    const response = await axios.post(`${RECON_API_BASE}/api/recon`, { target })
    res.json(response.data)
  } catch (err: any) {
    console.error('[recon/start]', err.message)
    res.status(500).json({ error: 'Failed to connect to GEMINIRECON service' })
  }
})

/**
 * Get recon health/status
 * GET /v1/recon/status
 */
reconRoutes.get('/status', async (_req, res) => {
  try {
    const response = await axios.get(`${RECON_API_BASE}/`)
    res.json(response.data)
  } catch (err: any) {
    res.status(500).json({ status: 'offline', error: err.message })
  }
})
