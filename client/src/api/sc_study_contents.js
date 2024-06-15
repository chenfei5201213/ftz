import request from '@/utils/request'

export function getScStudyContentById(id) {
  return request({
    url: `/ftz/sc/study_content/${id}/`, method: 'get'
  })
}

export function getScStudyContentList(query) {
  return request({
    url: '/ftz/sc/study_content/', method: 'get', params: query
  })
}

export function createScStudyContent(data) {
  return request({
    url: '/ftz/sc/study_content/', method: 'post', data
  })
}

export function updateScStudyContent(id, data) {
  return request({
    url: `/ftz/sc/study_content/${id}/`, method: 'put', data
  })
}

export function deleteScStudyContent(id) {
  return request({
    url: `/ftz/sc/study_content/${id}/`, method: 'delete'
  })
}
