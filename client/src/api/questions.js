import request from '@/utils/request'

export function getQuestionsById(id) {
  return request({
    url: `/ftz/survey/questions/${id}/`, method: 'get'
  })
}

export function getQuestionsList(query) {
  return request({
    url: '/ftz/survey/questions/', method: 'get', params: query
  })
}

export function createQuestions(data) {
  return request({
    url: '/ftz/survey/questions/', method: 'post', data
  })
}

export function updateQuestions(id, data) {
  return request({
    url: `/ftz/survey/questions/${id}/`, method: 'put', data
  })
}

export function deleteQuestions(id) {
  return request({
    url: `/ftz/survey/questions/${id}/`, method: 'delete'
  })
}
