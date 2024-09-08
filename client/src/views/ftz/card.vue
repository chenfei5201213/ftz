<template>
  <div class="app-container">
    <el-card>
      <div>
        <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增卡片</el-button>
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
        <el-select v-model="listQuery.type"
                   placeholder="卡片类型"
                   clearable
                   style="width: 120px">
          <el-option v-for="(item, index) in typeOptions" :key="index" :label="item.name"
                     :value="item.value"></el-option>
        </el-select>
        <el-select v-model="listQuery.difficulty"
                   placeholder="难度"
                   clearable
                   style="width: 120px">
          <el-option v-for="(item, index) in difficultyOptions" :key="index" :label="item.name"
                     :value="item.value"></el-option>
        </el-select>
        <el-input
          v-model="listQuery.search"
          placeholder="输入关键字搜索"
          style="width: 300px"
          class="filter-item"
        />
        <!--        <el-input v-model="listQuery.field110" style="width: 120px" placeholder="输入卡片ID"></el-input>-->
        <!--        <el-input v-model="listQuery.field110" style="width: 150px" placeholder="卡片完整名称"></el-input>-->
        <el-button
          class="filter-item"
          type="primary"
          icon="el-icon-search"
          @click="resetFilter"
        >查询
        </el-button
        >
      </div>
    </el-card>

    <el-table
      v-loading="listLoading"
      :data="
        tableDataList.results"
      style="width: 100%; margin-top: 10px"
      highlight-current-row
      row-key="id"
      height="100"
      stripe
      border
      v-el-height-adaptive-table="{ bottomOffset: 50 }"
    >
      <el-table-column label="ID" width="60">
        <template slot-scope="scope">{{ scope.row.id }}</template>
      </el-table-column>
      <el-table-column label="标题">
        <template slot-scope="scope">{{ scope.row.title }}</template>
      </el-table-column>
      <el-table-column label="类型">
        <template slot-scope="scope">{{ scope.row.type_description }}</template>
      </el-table-column>
      <el-table-column label="分组">
        <template slot-scope="scope">{{ scope.row.group_name }}</template>
      </el-table-column>
      <el-table-column label="难度">
        <template slot-scope="scope">{{ scope.row.difficulty_description }}</template>
      </el-table-column>
      <el-table-column label="话题">
        <template slot-scope="scope">{{ scope.row.topic }}</template>
      </el-table-column>
      <el-table-column label="状态">
        <template slot-scope="scope">{{ scope.row.status_description }}</template>
      </el-table-column>
      <el-table-column label="预览链接">
        <template slot-scope="scope">{{ scope.row.id }}</template>
      </el-table-column>

      <el-table-column align="center" label="操作">
        <template slot-scope="scope">
          <el-button
            type="primary"
            size="small"
            icon="el-icon-edit"
            :disabled="!checkPermission(['position_update'])"
            @click="handleEdit(scope)"
          />
          <el-button
            type="danger"
            size="small"
            icon="el-icon-delete"
            :disabled="!checkPermission(['position_delete'])"
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
      :title="dialogType === 'edit' ? '编辑卡片' : '新增卡片'"
    >
      <el-form
        ref="Form"
        :model="tableData"
        label-width="80px"
        label-position="right"
      >
        <el-form-item label="卡片标题" prop="title">
          <el-input v-model="tableData.title" placeholder="卡片标题"/>
        </el-form-item>
        <el-form-item label="卡片类型" prop="type">
          <el-select
            v-model="tableData.type"
            placeholder="请选择"
            style="width: 90%"
          >
            <el-option
              v-for="item in typeOptions"
              :key="item.value"
              :label="item.name"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="分组" prop="group_name">
          <el-input v-model="tableData.group_name" placeholder="分组"/>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="tableData.status">
            <el-radio label=0>下线</el-radio>
            <el-radio label=1>上线</el-radio>
          </el-radio-group>
        </el-form-item>
        <!-- todo 这里要支持图片上传，然后将相对路径赋值-> 多选 -->
        <el-form-item label="核心图" prop="card_core_image">
          <el-upload
            class="avatar-uploader"
            :action="upUrl"
            accept="image/jpeg, image/gif, image/png, image/bmp"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
            :headers="upHeaders"
          >
            <img v-if="tableData.card_core_image" :src="tableData.card_core_image" class="avatar"/>
            <i v-else class="el-icon-plus avatar-uploader-icon"/>
          </el-upload>
        </el-form-item>
        <el-form-item label="话题" prop="topic">
          <el-input v-model="tableData.topic" placeholder="话题"/>
        </el-form-item>
        <el-row>
          <el-col :span="12">
            <el-form-item label="难度" prop="difficulty">
          <el-select
            v-model="tableData.difficulty"
            placeholder="请选择"
            style="width: 90%"
          >
            <el-option
              v-for="item in difficultyOptions"
              :key="item.value"
              :label="item.name"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学习时长" prop="study_duration">
            <el-input-number v-model="tableData.study_duration" :min="1" :max="1000" :step="1">
            </el-input-number>
            </el-form-item></el-col>
        </el-row>
        <!-- todo 这里需要支持获取素材列表，搜索-> 多选 -->
        <el-form-item label="关联素材" prop="study_materials">
          <el-scrollbar>
            <el-select
              v-model="tableData.study_materials"
              :multiple="true"
              :filterable="true"
              reserve-keyword
              placeholder="请输入素材名称关键词"
              :remote-method="remoteGetMaterials"
              style="width: 90%"
            >
              <el-option
                v-for="item in materialData"
                :key="item.id"
                :label="item.title"
                :value="item.id"
              />
            </el-select>
          </el-scrollbar>
        </el-form-item>
        <el-form-item label="关联单词" prop="study_materials">
          <el-scrollbar>
            <el-select
              v-model="tableData.words"
              :multiple="true"
              :filterable="true"
              reserve-keyword
              placeholder="请输入素材名称关键词"
              :remote-method="remoteGetMaterials"
              style="width: 90%"
            >
              <el-option
                v-for="item in materialData"
                :key="item.id"
                :label="item.title"
                :value="item.id"
              />
            </el-select>
          </el-scrollbar>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="tableData.description" placeholder="课程描述" :autosize="{ minRows: 2, maxRows: 4 }"
                    type="textarea"/>
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button type="danger" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirm('Form')">确认</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import {
  getCardById,
  getCardList,
  createCard,
  updateCard,
  deleteCard
} from "@/api/card";
import checkPermission from "@/utils/permission";
import {upUrl, upHeaders} from "@/api/file";
import {getEnumConfigList} from "@/api/enum_config";
import {getMaterialSimpleList} from "@/api/material";
import {getCourseList} from "@/api/course";
import {getLessonList} from "@/api/lesson";

const defaultM = {
  title: "",
  type: "",
  description: "",
  status: 0,
  card_core_image: "",
  group_name: "",
  topic: "",
  difficulty: "",
  study_materials: []
};
export default {
  data() {
    return {
      courseList: [],
      courseId: '',
      lessonList: [],
      lessonId: '',
      courseSearch: {},
      lessonSearch: {},
      upHeaders: upHeaders(),
      upUrl: upUrl(),
      tableData: {
        id: "",
        title: "",
        type: "",
        description: "",
        status: 0,
        card_core_image: "",
        group_name: "",
        topic: "",
        difficulty: "",
        study_materials: []
      },
      search: "",
      tableDataList: [],
      listLoading: true,
      dialogVisible: false,
      dialogType: "new",
      difficultyOptions: [],
      typeOptions: [],
      listQuery: {
        page: 1,
        page_size: 20,
      },
      module_name: 'card',
      materialData: [],
    }
  },
  computed: {},
  created() {
    this.getList();
    this.getCardTypeList();
    this.getDifficultyList();
    this.getCourseData()
    this.getLessonData()
  },
  methods: {
    changeGetLessonList() {
      this.lessonSearch.course_id = this.courseId;
      this.getLessonData();
    },
    clearGetList() {
      this.courseId = '';
      this.lessonId = '';
      this.listQuery.card_ids = '';
      this.getList();
    },
    changeGetCardList() {
      const selectedLesson = this.lessonList.find(lesson => lesson.id === this.lessonId);
      this.listQuery.card_ids = selectedLesson.cards;
      this.getList();
    },
    getCourseData() {
      return new Promise((resolve, reject) => {
        getCourseList(this.courseSearch).then((response) => {
          this.courseList = response.data.results;
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
    checkPermission,
    getCardTypeList() {
      let query = {module: this.module_name, service: 'type'};
      getEnumConfigList(query).then((response) => {
        this.typeOptions = response.data.results;
      })
    },
    remoteGetMaterials(query_str) {
      getMaterialSimpleList({'search': query_str}).then((response) => {
        this.materialData = response.data;
      })
    },
    getMaterialDataList() {
      getMaterialSimpleList().then((response) => {
        this.materialData = response.data;
      })
    },
    getDifficultyList() {
      let query = {module: this.module_name, service: 'difficulty'};
      getEnumConfigList(query).then((response) => {
        this.difficultyOptions = response.data.results;
      })
    },
    handleAvatarSuccess(res) {
      console.log(res)
      this.tableData.card_core_image = res.data.file
    },
    beforeAvatarUpload(file) {
      const isLt2M = file.size / 1024 / 1024 < 2;
      if (!isLt2M) {
        this.$message.error("上传核心图片大小不能超过 2MB!");
      }
      return isLt2M;
    },
    getList(page) {
      this.listQuery.page = page;
      this.listLoading = true;
      getCardList(this.listQuery).then((response) => {
        this.tableDataList = response.data;
        this.listLoading = false;
      })
    },
    resetFilter() {
      this.getList()
    },
    handleAdd() {
      this.tableData = Object.assign({}, defaultM)
      this.dialogType = "new"
      this.dialogVisible = true
      this.getMaterialDataList()
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate()
      })
    },
    handleEdit(scope) {
      this.tableData = Object.assign({}, scope.row) // copy obj
      this.dialogType = "edit"
      this.dialogVisible = true
      this.getMaterialDataList()
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate()
      })
    },
    handleDelete(scope) {
      this.$confirm("确认删除?", "警告", {
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        type: "error"
      })
        .then(async () => {
          await deleteCard(scope.row.id);
          this.getList()
          this.$message({
            type: "success",
            message: "删除成功!"
          })
        })
        .catch((err) => {
          console.error(err)
        })
    },
    async confirm(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          const isEdit = this.dialogType === "edit"
          if (isEdit) {
            updateCard(this.tableData.id, this.tableData).then(() => {
              this.getList()
              this.dialogVisible = false;
              this.$message({
                message: "编辑成功",
                type: "success"
              })
            })
          } else {
            createCard(this.tableData).then((res) => {
              this.getList()
              this.dialogVisible = false
              this.$message({
                message: "新增成功",
                type: "success"
              })
            })
          }
        } else {
          return false
        }
      })
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
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
}

.el-select-dropdown {
  overflow-y: auto; /* 添加这个样式 */
}

.avatar {
  width: 100px;
  height: 100px;
  display: block;
}
</style>
