import request from '@/utils/request'

export function getProductById(id) {
  return request({
    url: `/mall/product/${id}/`, method: 'get'
  })
}

export function getProductList(query) {
  return request({
    url: '/mall/product/', method: 'get', params: query
  })
}

export function createProduct(data) {
  return request({
    url: '/mall/product/', method: 'post', data
  })
}

export function updateProduct(id, data) {
  return request({
    url: `/mall/product/${id}/`, method: 'put', data
  })
}

export function deleteProduct(id) {
  return request({
    url: `/mall/product/${id}/`, method: 'delete'
  })
}
