import request from '@/utils/request'

export function getOrderById(id) {
  return request({
    url: `/mall/order/${id}/`, method: 'get'
  })
}

export function getOrderList(query) {
  return request({
    url: '/mall/order/', method: 'get', params: query
  })
}

export function createOrder(data) {
  return request({
    url: '/mall/order/', method: 'post', data
  })
}

export function updateOrder(id, data) {
  return request({
    url: `/mall/order/${id}/`, method: 'put', data
  })
}

export function deleteOrder(id) {
  return request({
    url: `/mall/order/${id}/`, method: 'delete'
  })
}
