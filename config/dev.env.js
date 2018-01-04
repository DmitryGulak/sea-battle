'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  BASE_URL: '"http://127.0.0.1:5000"',
  ACCESS_TOKEN: '"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImRpbW9uaWt5cyIsInVzZXJfdG9rZW4iOiIwMDJkZDE5MDMwN2Y0YmRiYjk3ZjViNjI1NDM0YTJiYyJ9.OhGg5JS216Ymq0n8gnCyfKcDLJcr0cX71xPhgrx7rcI"'
})
