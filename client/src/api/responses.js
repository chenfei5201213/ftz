import request from '@/utils/request'

export function getResponsesById(id) {
  return request({
    url: `/ftz/survey/responses/${id}/`, method: 'get'
  })
}

export function getResponsesList(query) {
  return request({
    url: '/ftz/survey/responses/', method: 'get', params: query
  })
}

export function createResponses(data) {
  return request({
    url: '/ftz/survey/responses/', method: 'post', data
  })
}

export function updateResponses(id, data) {
  return request({
    url: `/ftz/survey/responses/${id}/`, method: 'put', data
  })
}

export function deleteResponses(id) {
  return request({
    url: `/ftz/survey/responses/${id}/`, method: 'delete'
  })
}
