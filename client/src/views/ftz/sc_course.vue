<template>
  <div class="app-container">
    <el-card>
      <div>
        <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增期课</el-button>
        <el-select v-model="course" placeholder="请选择" clearable>
          <el-option
            v-for="item in courseList"
            :key="item.id"
            :label="`【${item.id}】- ${item.title} (${item.type})`"
            :value="item.id">
            <!--            <span style="float: right; color: #8492a6; font-size: 13px">{{ item.value }}</span>-->
          </el-option>
        </el-select>
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
        tableDataList.results.filter(
          (data) =>
            !search || data.title.toLowerCase().includes(search.toLowerCase())
        )
      "
      style="width: 100%; margin-top: 10px"
      highlight-current-row
      row-key="id"
      height="100"
      stripe
      border
      v-el-height-adaptive-table="{ bottomOffset: 50 }"
    >
      <el-table-column label="期课ID" width="60">
        <template slot-scope="scope">{{ scope.row.id }}</template>
      </el-table-column>
      <el-table-column label="课程ID">
        <template slot-scope="scope">{{ scope.row.course }}</template>
      </el-table-column>
      <el-table-column label="期课类型">
        <template slot-scope="scope">{{ scope.row.term_type }}</template>
      </el-table-column>
      <el-table-column label="期数">
        <template slot-scope="scope">{{ scope.row.term_number }}</template>
      </el-table-column>
      <el-table-column label="课程版本">
        <template slot-scope="scope">{{ scope.row.version }}</template>
      </el-table-column>
      <el-table-column label="天数">
        <template slot-scope="scope">{{ scope.row.total_days }}</template>
      </el-table-column>
      <el-table-column label="报名开始时间">
        <template slot-scope="scope">
          <span>{{ scope.row.enrollment_start }}</span>
        </template>
      </el-table-column>
      <el-table-column label="开课时间">
        <template slot-scope="scope">
          <span>{{ scope.row.course_start }}</span>
        </template>
      </el-table-column>
      <el-table-column label="老师">
        <template slot-scope="scope">{{ scope.row.teacher }}</template>
      </el-table-column>
      <el-table-column label="老师二维码">
        <template slot-scope="scope">{{ scope.row.teacher_qr_code }}</template>
      </el-table-column>
      <el-table-column align="center" label="操作">
        <template slot-scope="scope">
          <el-button
            type="primary"
            size="mini"
            icon="el-icon-edit"
            :disabled="!checkPermission(['position_update'])"
            @click="handleEdit(scope)"
          />
          <el-button
            type="danger"
            size="mini"
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
      :layout="prev,pager,next"
      :current-page.sync="listQuery.page"
      @current-change="getList"
    ></el-pagination>
    <el-dialog
      :visible.sync="dialogVisible"
      :title="dialogType === 'edit' ? '编辑问题' : '新增问题'"
    >
      <el-form
        ref="Form"
        :model="tableData"
        label-width="100px"
        label-position="right"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="课程" prop="course">
              <el-select v-model="tableData.course" placeholder="请选择">
                <el-option
                  v-for="item in courseList"
                  :key="item.id"
                  :label="`【${item.id}】- ${item.title} (${item.type})`"
                  :value="item.id">
                  <!--            <span style="float: right; color: #8492a6; font-size: 13px">{{ item.value }}</span>-->
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="期数" prop="term_number">
              <el-input v-model="tableData.term_number" placeholder="期数"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="课程天数" prop="total_days">
              <el-input v-model="tableData.total_days" placeholder="课程天数"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="课程版本" prop="version">
              <el-input v-model="tableData.version" placeholder="课程版本"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="老师名称" prop="teacher">
              <el-input v-model="tableData.teacher" placeholder="老师名称"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="助教老师名称" prop="assistant_teacher">
              <el-input v-model="tableData.assistant_teacher" placeholder="助教老师名称"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="老师二维码" prop="teacher_qr_code">
              <el-upload
                class="avatar-uploader"
                :action="upUrl"
                accept="image/jpeg, image/gif, image/png, image/bmp"
                :show-file-list="false"
                :on-success="handleAvatarSuccess"
                :before-upload="beforeAvatarUpload"
                :headers="upHeaders"
              >
                <img v-if="tableData.teacher_qr_code" :src="tableData.teacher_qr_code" class="avatar"/>
                <i v-else class="el-icon-plus avatar-uploader-icon"/>
              </el-upload>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="助教老师二维码" prop="assistant_teacher_qr_code">
              <el-upload
                class="avatar-uploader"
                :action="upUrl"
                accept="image/jpeg, image/gif, image/png, image/bmp"
                :show-file-list="false"
                :on-success="handleAvatarass"
                :before-upload="beforeAvatarUpload"
                :headers="upHeaders"
              >
                <img v-if="tableData.assistant_teacher_qr_code" :src="tableData.assistant_teacher_qr_code" class="avatar"/>
                <i v-else class="el-icon-plus avatar-uploader-icon"/>
              </el-upload>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="报名开始时间" prop="enrollment_start">
              <el-date-picker v-model="tableData.enrollment_start" placeholder="报名开始时间" type="datetime"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="报名结束时间" prop="enrollment_end">
              <el-date-picker v-model="tableData.enrollment_end" placeholder="报名结束时间" type="datetime"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="课程开始时间" prop="course_start">
              <el-date-picker v-model="tableData.course_start" placeholder="课程开始时间" type="datetime"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="课程结束时间" prop="course_end">
              <el-date-picker v-model="tableData.course_end" placeholder="课程结束时间" type="datetime"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="课程类型" prop="term_type">
              <el-input v-model="tableData.term_type" placeholder="课程类型"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
          </el-col>
          <el-col :span="12">
          </el-col>
        </el-row>
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
  getCourseList,
} from "@/api/course";
import {
  getScCourseById,
  getScCourseList,
  createScCourse,
  updateScCourse,
  deleteScCourse
} from "@/api/sc_course";
import {genTree, deepClone} from "@/utils";
import {upUrl, upHeaders} from "@/api/file";
import checkPermission from "@/utils/permission";
import {getEnumConfigList} from "@/api/enum_config";

const defaultM = {};
export default {
  data() {
    return {
      upHeaders: upHeaders(),
      upUrl: upUrl(),
      tableData: {
        id: "",
        question_type: "",
        question_text: "",
        options: "",
        survey: "",
        create_time: "",
        update_time: ""
      },
      search: "",
      tableDataList: {},
      listLoading: true,
      dialogVisible: false,
      dialogType: "new",
      courseList: [],
      course: null,
      listQuery: {
        page: 1,
        page_size: 20,
        search: null
      },
      enumConfigQuery: {
        module: 'course',
        service: 'type'
      }
    };
  },
  computed: {},
  created() {
    this.getCourseList().then(() => {
      this.getList();
    });

  },
  methods: {
    checkPermission,
    handleAvatarSuccess(res) {
      this.tableData.teacher_qr_code = res.data.file
    },
    beforeAvatarUpload(file) {
      const isLt2M = file.size / 1024 / 1024 < 2;
      if (!isLt2M) {
        this.$message.error("二维码大小不能超过 2MB!");
      }
      return isLt2M;
    },
    handleAvatarass(res) {
      this.tableData.assistant_teacher_qr_code = res.data.file
    },
    getCourseList() {
      return new Promise((resolve, reject) => {
        getCourseList({}).then((response) => {
          this.courseList = response.data.results;
          if (this.courseList && this.courseList.length > 0) {
            this.course = this.courseList[0].id;
          }
          resolve()
        })
      })
    },
    getList() {
      this.listLoading = true;
      this.listQuery.course = this.course;
      getScCourseList(this.listQuery).then((response) => {
        this.tableDataList = response.data;
        this.tableData = response.data;
        this.listLoading = false;
      });
    },
    resetFilter() {
      this.getList();
    },
    handleFilter() {
      const newData = this.tableDataList.filter(
        (data) =>
          !this.search ||
          data.title.toLowerCase().includes(this.search.toLowerCase())
      );
      this.tableData = genTree(newData);
    },
    handleAdd() {
      this.tableData = Object.assign({}, defaultM);
      this.dialogType = "new";
      this.dialogVisible = true;
      this.tableData.survey = this.course;
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate();
      });
    },
    handleEdit(scope) {
      this.tableData = Object.assign({}, scope.row); // copy obj
      this.dialogType = "edit";
      this.dialogVisible = true;
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate();
      });
    },
    handleDelete(scope) {
      this.$confirm("确认删除?", "警告", {
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        type: "error",
      })
        .then(async () => {
          await deleteScCourse(scope.row.id);
          this.getList();
          this.$message({
            type: "success",
            message: "成功删除!",
          });
        })
        .catch((err) => {
          console.error(err);
        });
    },
    goToQuestionsPage(scope) {
      this.$router.push({name: 'questions', params: scope});
    },
    async confirm(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          const isEdit = this.dialogType === "edit";
          if (isEdit) {
            updateScCourse(this.tableData.id, this.tableData).then(() => {
              this.getList();
              this.dialogVisible = false;
              this.$message({
                message: "编辑成功",
                type: "success",
              });
            });
          } else {
            createScCourse(this.tableData).then((res) => {
              this.getList();
              this.dialogVisible = false;
              this.$message({
                message: "新增成功",
                type: "success",
              });
            });
          }
        } else {
          return false;
        }
      });
    },
  },
};
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

.avatar {
  width: 100px;
  height: 100px;
  display: block;
}
</style>
