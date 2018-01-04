import axios from 'axios'

function getCookie (title) {
  const getValueFromJoinString = (text, title, start = '=', finish = ';') => {
    if (text) {
      const reg = new RegExp(`(?:^|${finish})\\s*${title}${start}([^${finish}]*)${finish}`)
      return (reg.exec(text) || [])[1] || ''
    }
    return ''
  }
  return getValueFromJoinString(document.cookie, title)
}

let accessToken = ''
let headers = {}

if (process.env.NODE_ENV === 'development') {
  axios.defaults.baseURL = process.env.BASE_URL
  headers = {
    'Content-Type': 'application/json',
    'X-Access-Token': process.env.ACCESS_TOKEN
  }
  accessToken = process.env.ACCESS_TOKEN.toString()
} else {
  axios.defaults.baseURL = ''
  headers = {
    'Content-Type': 'application/json'
  }
  accessToken = getCookie('user_token')
}

console.log('your access token is: ', accessToken)

function processError (error) {
  console.log('Error: ', error.response)
}

const gameMethods = {
  createGame (mode, cb, errCb) {
    axios.post('/api/create_game', null, {
      headers: headers,
      data: {
        mode: mode
      }
    }).then((response) => {
      cb(response)
    }).catch((error) => {
      processError(error)
      errCb(error)
    })
  },
  joinGame (gameId, cb, errCb) {
    let payload = {
      'game_id': gameId
    }
    axios.post('/api/join_game', null, {
      headers: headers,
      data: payload
    }).then((response) => {
      cb(response)
    }).catch((error) => {
      processError(error)
      errCb(error)
    })
  }
}

const userMethods = {
  getUser (cb, errCb) {
    axios.get('/api/get_user', {
      headers: headers
    }).then((response) => {
      cb(response)
    }).catch((error) => {
      processError(error)
      errCb(error)
    })
  },
  setUser (payload, cb, errCb) {
    axios.post('/api/set_user', null, {
      data: payload,
      headers: headers
    }).then((response) => {
      cb(response)
    }).catch((error) => {
      processError(error)
      errCb(error)
    })
  }
}

export default {
  ...userMethods,
  ...gameMethods
}
