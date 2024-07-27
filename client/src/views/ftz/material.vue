<template>
  <div class="app-container">
    <el-card>
      <div>
        <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增素材</el-button>
        <el-select v-model="courseId" placeholder="选择课程"
                   @change="changeGetLessonList"
                   @clear="clearGetList"
                   clearable style="width: 280px">
          <el-option v-for="(item, index) in courseList"
                     :key="index"
                     :label="`【${item.id}】- ${item.title} (${item.type})`"
                     :value="item.id">

          </el-option>
        </el-select>
        <el-select v-model="lessonId" placeholder="选择课时"
                   @change="changeGetCardList"
                   @clear="clearGetList"
                   clearable style="width: 200px">
          <el-option v-for="(item, index) in lessonList"
                     :key="index"
                     :label="`【${item.id}】- ${item.title} (${item.type})`"
                     :value="item.id">

          </el-option>
        </el-select>
        <el-select v-model="listQuery.type" placeholder="素材类型" clearable style="width: 120px">
          <el-option v-for="(item, index) in typeOptions" :key="index" :label="item.name" :value="item.value"></el-option>
        </el-select>
        <el-input v-model="listQuery.search" style="width: 300px" placeholder="输入关键字搜索"></el-input>
        <el-button class="filter-item" type="primary" icon="el-icon-search" @click="resetFilter">查询</el-button>
      </div>
    </el-card>
    <el-table
      v-loading="listLoading"
      :data="
        tableDataList.results.filter(
          (data) =>
            !this.listQuery.search || data.title.toLowerCase().includes(this.listQuery.search.toLowerCase())
        )
      "
      style="width: 100%; margin-top: 10px"
      highlight-current-row
      row-key="id"
      height="100" stripe border
      v-el-height-adaptive-table="{ bottomOffset: 50 }">
    <el-table-column label="ID" width="60">
      <template slot-scope="scope">{{ scope.row.id }}</template>
    </el-table-column>
    <el-table-column label="素材类型">
      <template slot-scope="scope">{{ scope.row.type_description }}</template>
    </el-table-column>
    <el-table-column label="标题">
      <template slot-scope="scope">{{ scope.row.title }}</template>
    </el-table-column>
    <el-table-column label="创建日期">
      <template slot-scope="scope">
        <span>{{ scope.row.create_time }}</span>
      </template>
    </el-table-column>
    <el-table-column label="创建更新时间">
       <template slot-scope="scope">
        <span>{{ scope.row.update_time }}</span>
      </template>
    </el-table-column>
      <el-table-column align="center" label="操作">
        <template slot-scope="scope">
          <el-button
            type="primary"
            size="small"
            icon="el-icon-edit"
            :disabled="checkPermission(['position_update'])"
            @click="handleEdit(scope)"
          />
          <el-button
            type="info"
            size="small"
            :disabled="checkPermission(['position_delete'])"
            @click="copyEdit(scope)"
          >复制</el-button>
          <el-button
            type="danger"
            size="small"
            icon="el-icon-delete"
            :disabled="checkPermission(['position_delete'])"
            @click="handleDelete(scope)"
          />
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
          v-show="tableDataList.count>0"
          :total="tableDataList.count"
          :page-size.sync="listQuery.page_size"
          :current-page.sync="listQuery.page"
          @current-change="getList"
        ></el-pagination>
    <el-dialog
      :visible.sync="dialogVisible"
      :title="dialogType === 'edit' ? '编辑素材' : '新增素材'">
      <el-form :model="readyData" label-width="110px" label-position="right">
        <el-form-item label="标题" prop="title">
          <el-input v-model="tableData.title" placeholder="标题" />
        </el-form-item>
        <el-form-item label="素材类型" prop="type">
          <el-select @change="changeType" v-model="tableData.type" placeholder="请选择" style="width: 100%">
            <el-option v-for="(item,index) in typeOptions" :label="item.name" :value="item.value" />
          </el-select>
        </el-form-item>
        <block v-if="type >=0">
          <block v-for="(item) in fileData">
            <el-form-item :label="item.label" :prop="item.col">
              <block v-if="item.type == 'file' ">
                <el-upload
                  class="avatar-uploader" v-if="item.col == 'file1'"
                  :action="upUrl"
                  accept="image/jpeg, image/gif, image/png, image/bmp"
                  :show-file-list="false"
                  :on-success="handleAvatarSuccess"
                  :before-upload="beforeAvatarUpload"
                  :headers="upHeaders"
                >
                  <img v-if="readyData.file1" :src="readyData.file1" class="avatar" />
                  <i v-else class="el-icon-plus avatar-uploader-icon" />
                </el-upload>
                <el-upload
                  class="avatar-uploader" v-if="item.col == 'file2'"
                  :action="upUrl"
                  accept="image/jpeg, image/gif, image/png, image/bmp"
                  :show-file-list="false"
                  :on-success="handleAvatarSuccess2"
                  :before-upload="beforeAvatarUpload"
                  :headers="upHeaders"
                >
                  <img v-if="readyData.file2" :src="readyData.file2" class="avatar" />
                  <i v-else class="el-icon-plus avatar-uploader-icon" />
                </el-upload>
              </block>
              <block v-if="item.type == 'char'">
                <el-input v-model="readyData[item.col]" :placeholder="item.label"/>
              </block>
              <block v-if="item.type == 'select'">
                <el-select v-model="readyData[item.col]" placeholder="请选择" width="100%">
                  <el-option v-for="(item,index) in tagsOptions" :key="item.value" :label="item.name" :value="index"/>
                </el-select>
              </block>
              <block v-if="item.type == 'select1'">
                <el-select v-model="readyData[item.col]" placeholder="请选择" width="100%">
                  <el-option v-for="(item,index) in fileOptions" :key="item.value" :label="item.name" :value="index"/>
                </el-select>
              </block>
              <block v-if="item.type == 'content'">
                <VueEditor v-model="readyData[item.col]"></VueEditor>
              </block>
              <block v-if="item.type == 'video'">
                <el-upload class="avatar-uploader" :action="upUrl" :show-file-list="true" v-if="item.col == 'video1'"
                  :on-success="handleAvatarSuccessVideo"
                  :before-upload="beforeAvatarUploadVideo"
                  :headers="upHeaders">
                  <i v-if="readyData.video1" class="el-icon-video-play avatar-uploader-icon" />
                  <i v-else class="el-icon-plus avatar-uploader-icon" />
                </el-upload>
                <el-upload class="avatar-uploader" :action="upUrl" :show-file-list="true" v-if="item.col == 'video2'"
                  :on-success="handleAvatarSuccessVideo2"
                  :before-upload="beforeAvatarUploadVideo"
                  :headers="upHeaders">
                  <i v-if="readyData.video2" class="el-icon-video-play avatar-uploader-icon" />
                  <i v-else class="el-icon-plus avatar-uploader-icon" />
                </el-upload>
              </block>
            </el-form-item>
          </block>
        </block>
        <el-form-item>
          <el-button type="primary" @click="onsubmit">提交</el-button>
          <el-button @click="dialogVisible = false">取消</el-button>
        </el-form-item>
      </el-form>
  </el-dialog>
  </div>
</template>

<script>
import {VueEditor} from "vue2-editor";
import {
  getMaterialById,
  getMaterialList,
  createMaterial,
  updateMaterial,
  deleteMaterial
} from '@/api/material'
import {getCourseList} from "@/api/course";
import {getLessonList} from "@/api/lesson";
import {getCardList} from "@/api/card";
import { genTree, deepClone } from '@/utils'
import { checkPermission } from '@/utils/permission'
import { upUrl, upHeaders } from '@/api/file'

const defaultM = {
  id: '',
  type: '',
  datas: {}
}
export default {
  components : {
    VueEditor
  },
  data() {
    return {
      courseList: [],
      courseId: '',
      lessonList: [],
      lessonId: '',
      courseSearch: {},
      lessonSearch: {},
      cardSearch: {},
      upHeaders: upHeaders(),
      upUrl: upUrl(),
      tableData: {
        id: '',
        type: '',
        title: '',
        context: {}
      },
      addData: {},
      readyData: {
        file1: '',
        file2: '',
        video1: '',
        video2: '',
        char1: '',
        char2: '',
        char3: '',
        char4: '',
        char5: '',
        char6: '',
        char7: '',
        char8: '',
        content1: '',
        content2: '',
        num: ''
      },
      fileData: [],
      tableDataList: [],
      listLoading: true,
      dialogVisible: false,
      tagsOptions: [{value:'1',name:'第一模块过渡页'},{value:'2',name:'第二模块过渡页'},{value:'3',name:'第三模块过渡页'}],
      fileOptions: [{value:'1',name:'音频'},{value:'2',name:'视频'},{value:'3',name:'图文'}],
      dialogType: 'new',
      type: '',
      typeOptions: [//file 图片 content富文本 char文字 video音频
        {value:'0',name:'问卷',datas:[{label:'问卷图文',col:'file1',type:'file'},{label:'富文本内容',col:'content1',type:'content'}]},
        {value:'1',name:'50音卡片展示页A',datas:[{label:'单词图片',col:'file1',type:'file'},{label:'音频',col:'video1',type:'video'},{label: '图片',col:'file2',type:'file'},{label:'汉字',col:'content1',type:'content'},{label:'片假名',col:'content2',type:'content'}]},
        {value:'2',name:'50音卡片展示页B',datas:[{label:'配置图片',col:'file1',type:'file'},{label:'罗马音',col:'char1',type:'char'},{label:'词源',col:'char2',type:'char'},{label:'单词发音',col:'video1',type:'video'},{label:'发音技巧',col:'content1',type:'content'},{label:'单词',col:'content2',type:'content'}]},
        {value:'3',name:'单词卡A面',datas:[{label:'配置图片',col:'file1',type:'file'},{label:'音频',col:'video1',type:'video'},{label:'图片',col:'file2',type:'file'},{label:'句子',col:'content1',type:'content'}]},
        {value:'4',name:'单词卡B面',datas:[{label:'单词图片',col:'file1',type:'file'},{label:'词性',col:'char1',type:'char'},{label:'含义',col:'char2',type:'char'},{label:'常见搭配音频',col:'video1',type:'video'},{label:'例句发音',col:'video2',type:'video'},{label:'常见搭配',col:'content1',type:'content'},{label:'例句',col:'content2',type:'content'}]},
        {value:'5',name:'语法卡A面',datas:[{label:'文法图片',col:'file1',type:'file'},{label:'示意图片',col:'file2',type:'file'}]},
        {value:'6',name:'语法卡B面',datas:[{label:'配置图片',col:'file1',type:'file'},{label:'慢速发音',col:'video1',type:'video'},{label:'快速发音',col:'video2',type:'video'},{label:'含义',col:'content1',type:'content'},{label:'例句',col:'content2',type:'content'}]},
        {value:'7',name:'板块过渡页',datas:[{label:'选择板块',col:'num',type:'select'},{label:'板块介绍文字',col:'content1',type:'content'}]},
        {value:'8',name:'图文选择题',datas:[{label:'问题描述',col:'char1',type:'char'},{label:'图片',col:'file1',type:'file'},{label:'选项文字',col:'char2',type:'char'},{label:'选项文字',col:'char3',type:'char'},{label:'答案文字',col:'char4',type:'char'}]},
        {value:'9',name:'文图选择题',datas:[{label:'问题描述',col:'char1',type:'char'},{label:'文字',col:'char2',type:'char'},{label:'选项图片',col:'file1',type:'file'},{label:'选项文字',col:'char3',type:'char'},{label:'选项图片',col:'file2',type:'file'},{label:'选项文字',col:'char4',type:'char'},{label:'答案文字',col:'char5',type:'char'}]},
        {value:'10',name:'文字选择题',datas:[{label:'问题描述',col:'char1',type:'char'},{label:'文字',col:'char2',type:'char'},{label:'选项文字',col:'char3',type:'char'},{label:'选项文字',col:'char4',type:'char'},{label:'答案文字',col:'char5',type:'char'}]},
        {value:'11',name:'语音文字选择题',datas:[{label:'问题描述',col:'char1',type:'char'},{label:'语音',col:'video1',type:'video'},{label:'选项文字',col:'char2',type:'char'},{label:'选项文字',col:'char3',type:'char'},{label:'答案文字',col:'char4',type:'char'}]},
        {value:'12',name:'语音图片选择题',datas:[{label:'问题描述',cl:'char1',type:'char'},{label:'语音',col:'video1',type:'video'},{label:'选项图片',col:'file1',type:'file'},{label:'选项文字',col:'char2',type:'char'},{label:'选项图片',col:'file2',type:'file'},{label:'选项文字',col:'char3',type:'char'},{label:'答案文字',col:'char4',type:'char'}]},
        {value:'13',name:'文字语音选择题',datas:[{label:'问题描述',col:'char1',type:'char'},{label:'文字',col:'char2',type:'char'},{label:'选项语音',col:'video1',type:'video'},{label:'选项文字',col:'char3',type:'char'},{label:'选项语音',col:'video2',type:'video'},{label:'选项文字',col:'char4',type:'char'},{label:'答案文字',col:'char5',type:'char'}]},
        {value:'14',name:'填空题',datas:[{label:'问题描述',col:'char1',type:'char'},{label:'翻译文字',col:'char2',type:'char'},{label:'正确文字顺序',col:'char3',type:'char'},{label:'预录制文字内容',col:'char4',type:'char'}]},
        {value:'15',name:'单词跟读',datas:[{label:'单词',col:'char1',type:'char'},{label:'片假名',col:'content1',type:'content'},{label:'文字解释',col:'char2',type:'char'},{label:'原始语音',col:'video1',type:'video'}]},
        {value:'16',name:'句子跟读页',datas:[{label:'日语句子',col:'char1',type:'char'},{label:'中文翻译',col:'char2',type:'char'},{label:'原始语音',col:'video1',type:'video'}]},
        {value:'17',name:'书写页',datas:[{label:'文字',col:'char1',type:'char'},{label:'读音',col:'video1',type:'video'},{label:'字帖中展示的文字',col:'char2',type:'char'}]},
        {value:'18',name:'连线页',datas:[{label:'汉字单词',col:'char1',type:'char'},{label:'日语单词',col:'char2',type:'char'},{label:'汉语单词',col:'char3',type:'char'},{label:'日语单词',col:'char4',type:'char'},{label:'汉语单词',col:'char5',type:'char'},{label:'日语单词',col:'char6',type:'char'},{label:'汉语单词',col:'char7',type:'char'},{label:'日语单词',col:'char8',type:'char'}]},
        {value:'19',name:'图文内容页',datas:[{label:'选择音视频类型',col:'num',type:'select1'},{label:'音视频素材',col:'video1',type:'video'},{label:'文字内容',col:'content1',type:'content'}]},
        {value:'20',name:'双图文内容页',datas:[{label:'图文素材1',col:'file1',type:'file'},{label:'图文素材2',col:'file2',type:'file'},{label:'文字内容',col:'content1',type:'content'}]},
        {value:'21',name:'纯文本页',datas:[{label:'文字内容',col:'content1',type:'content'}]},
        {value:'22',name:'文字选择题B',datas:[{label:'文字',col:'char1',type:'char'},{label:'选项文字',col:'char2',type:'char'},{label:'选项文字',col:'char3',type:'char'},{label:'答案文字',col:'char4',type:'char'}]}
      ],
      listQuery: {
        page: 1,
        page_size: 20,
        search: null
      }
    }
  },
  computed: {},
  created() {
    this.getCourseData()
    this.getLessonData()
    this.getList()
    this.clearData()
  },
  methods: {
    changeGetLessonList(){
      this.lessonSearch.course_id = this.courseId;
      this.getLessonData();
    },
    clearGetList(){
      this.courseId='';
      this.lessonId='';
      this.listQuery.ids='';
      this.getList();
    },
    changeGetCardList(){
      const selectedLesson = this.lessonList.find(lesson => lesson.id === this.lessonId);
      this.cardSearch.card_ids = selectedLesson.cards;
      getCardList(this.cardSearch).then((response) => {
          this.cardList = response.data.results;
          const combinedStudyMaterials = Array.prototype.concat.apply([], this.cardList.map(card => card.study_materials));
          this.listQuery.ids = combinedStudyMaterials
          this.getList();
        })
    },
    getCourseData() {
      return new Promise((resolve, reject) => {
        getCourseList(this.courseSearch).then((response) => {
          this.courseList = response.data.results;
          // if (this.courseList && this.courseList.length > 0) {
          //   this.courseId = this.courseList[0].id;
          // }
          resolve()
        })
      })
    },
    getLessonData() {
      return new Promise((resolve, reject) => {
        getLessonList(this.lessonSearch).then((response) => {
          this.lessonList = response.data.results;
          // if (this.lessonList && this.lessonList.length > 0) {
          //   this.lessonId = this.lessonList[0].id;
          // }
          resolve()
        })
      })
    },
    getCardData() {
      return new Promise((resolve, reject) => {
        getCardList(this.cardSearch).then((response) => {
          this.courseList = response.data.results;
          // if (this.courseList && this.courseList.length > 0) {
          //   this.courseId = this.courseList[0].id;
          // }
          resolve()
        })
      })
    },
    checkPermission,
    changeType(e) {
      this.fileData = this.typeOptions[e].datas
      var datas = this.typeOptions[e].datas
      for (var i = 0; i < datas.length; i++) {
        this.addData[datas[i].col] = ''
      }
    },
    handleAvatarSuccess(res) {
      this.readyData.file1 = res.data.file
    },
    handleAvatarSuccess2(res) {
      this.readyData.file2 = res.data.file
    },
    beforeAvatarUpload(file) {
      const isLt2M = file.size / 1024 / 1024 < 2
      if (!isLt2M) {
        this.$message.error('上传图片大小不能超过 2MB!')
      }
      return isLt2M
    },
    handleAvatarSuccessVideo(res) {
      console.log('video1', res)
      this.readyData.video1 = res.data.file
    },
    handleAvatarSuccessVideo2(res) {
      this.readyData.video2 = res.data.file
    },
    beforeAvatarUploadVideo(file) {
      const isLt2M = file.size / 1024 / 1024 < 15
      if (!isLt2M) {
        this.$message.error('上传文件大小不能超过 15MB!')
      }
      return isLt2M
    },
    getList(page) {
      this.listQuery.page = page
      this.listLoading = true
      getMaterialList(this.listQuery).then((response) => {
        this.tableDataList = response.data
        this.listLoading = false
      })
    },
    resetFilter() {
      this.getList(1);
    },
    handleFilter() {
      const newData = this.tableDataList.filter(
        (data) =>
          !this.search ||
          data.title.toLowerCase().includes(this.search.toLowerCase())
      )
      this.tableData = genTree(newData)
    },
    handleAdd() {
      this.tableData = Object.assign({}, defaultM)
      this.dialogType = 'new'
      this.dialogVisible = true
      this.clearData()
    },
    copyEdit(scope) {
      this.clearData()
      this.tableData = Object.assign({}, scope.row) // copy obj
      this.tableData.id = ''
      this.fileData = this.typeOptions[this.tableData.type].datas
      this.readyData = JSON.parse(this.tableData.context)
      this.dialogType = 'new'
      this.dialogVisible = true
    },
    handleEdit(scope) {
      this.clearData()
      this.tableData = Object.assign({}, scope.row) // copy obj
      this.fileData = this.typeOptions[this.tableData.type].datas
      this.readyData = JSON.parse(this.tableData.context)
      this.dialogType = 'edit'
      this.dialogVisible = true
    },
    handleDelete(scope) {
      this.$confirm('确认删除?', '警告', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'error'
      })
        .then(async() => {
          await deleteMaterial(scope.row.id)
          this.getList()
          this.$message({
            type: 'success',
            message: '删除成功!'
          })
        })
        .catch((err) => {
          console.error(err)
        })
    },
    onsubmit() {
      console.log(this.readyData)
      if (!this.tableData.title) {
        this.$message.error('标题不能为空')
        return
      }
      if (this.tableData.type >= 0 ) {
        for (let key in this.fileData) {
          var k = this.fileData[key].col
          this.addData[k] = this.readyData[k]
        }
        this.tableData.context = JSON.stringify(this.addData)
      } else {
        this.$message.error('请选择素材类型')
        return
      }
      console.log(this.tableData)
      this.addSubmit()
    },

    async addSubmit() {
      const isEdit = this.dialogType === 'edit'
      console.log(this.tableData);
      if (isEdit) {
        updateMaterial(this.tableData.id, this.tableData).then(() => {
          this.getList()
          this.dialogVisible = false
          this.$message({
            message: '编辑成功',
            type: 'success'
          })
        })
      } else {
        createMaterial(this.tableData).then((res) => {
          this.getList()
          this.dialogVisible = false
          this.$message({
            message: '新增成功',
            type: 'success'
          })
        })
      }
      this.clearData()
    },
    clearData() {
      this.type = ''
      this.fileData = {}
      this.addData = {}
      this.readyData = {
          file1: '',
          file2: '',
          video1: '',
          video2: '',
          char1: '',
          char2: '',
          char3: '',
          char4: '',
          char5: '',
          char6: '',
          char7: '',
          char8: '',
          content1: '',
          content2: '',
          num: ''
      }
    }
  }
}
</script>
<style scoped>
.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}
.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 60px;
  height: 60px;
  line-height: 60px;
  text-align: center;
  transform: translateY(-10px);
}
.avatar {
  width: 60px;
  height: 60px;
  display: block;
}
</style>
