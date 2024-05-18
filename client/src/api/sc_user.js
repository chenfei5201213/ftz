import request from '@/utils/request'

export function getScUserById(id) {
  return request({
    url: `/ftz/sc/user/${id}/`, method: 'get'
  })
}

export function getScUserList(query) {
  return request({
    url: '/ftz/sc/user/', method: 'get', params: query
  })
}

export function createScUser(data) {
  return request({
    url: '/ftz/sc/user/', method: 'post', data
  })
}

export function updateScUser(id, data) {
  return request({
    url: `/ftz/sc/user/${id}/`, method: 'put', data
  })
}

export function deleteScUser(id) {
  return request({
    url: `/ftz/sc/user/${id}/`, method: 'delete'
  })
}
