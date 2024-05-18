import request from '@/utils/request'

export function getScCourseById(id) {
  return request({
    url: `/ftz/sc/course/${id}/`, method: 'get'
  })
}

export function getScCourseList(query) {
  return request({
    url: '/ftz/sc/course/', method: 'get', params: query
  })
}

export function createScCourse(data) {
  return request({
    url: '/ftz/sc/course/', method: 'post', data
  })
}

export function updateScCourse(id, data) {
  return request({
    url: `/ftz/sc/course/${id}/`, method: 'put', data
  })
}

export function deleteScCourse(id) {
  return request({
    url: `/ftz/sc/course/${id}/`, method: 'delete'
  })
}
