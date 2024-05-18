import request from '@/utils/request'

export function getScStudyRecordById(id) {
  return request({
    url: `/ftz/sc/study_record/${id}/`, method: 'get'
  })
}

export function getScStudyRecordList(query) {
  return request({
    url: '/ftz/sc/study_record/', method: 'get', params: query
  })
}

export function createScStudyRecord(data) {
  return request({
    url: '/ftz/sc/study_record/', method: 'post', data
  })
}

export function updateScStudyRecord(id, data) {
  return request({
    url: `/ftz/sc/study_record/${id}/`, method: 'put', data
  })
}

export function deleteScStudyRecord(id) {
  return request({
    url: `/ftz/sc/study_record/${id}/`, method: 'delete'
  })
}
