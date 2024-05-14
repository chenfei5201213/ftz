import request from '@/utils/request'

export function getSurveyById(id) {
  return request({
    url: `/ftz/survey/survey/${id}/`, method: 'get'
  })
}

export function getSurveyList(query) {
  return request({
    url: '/ftz/survey/survey/', method: 'get', params: query
  })
}

export function createSurvey(data) {
  return request({
    url: '/ftz/survey/survey/', method: 'post', data
  })
}

export function updateSurvey(id, data) {
  return request({
    url: `/ftz/survey/survey/${id}/`, method: 'put', data
  })
}

export function deleteSurvey(id) {
  return request({
    url: `/ftz/survey/survey/${id}/`, method: 'delete'
  })
}
